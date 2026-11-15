# データソース完全リファレンス

## 課題タイプ別 最適ソース早見表

| 課題タイプ | 第1候補 | 第2候補 | 第3候補 |
|---|---|---|---|
| 人口・世帯・移動 | e-Stat（国勢調査） | RESAS | 川崎市統計書 |
| 子育て・保育 | e-Stat（社会福祉施設調査） | 川崎市オープンデータ | RESAS |
| 教育 | e-Stat（学校基本調査） | 川崎市・各県教委 | OECD Education |
| 高齢化・福祉 | e-Stat（社会保障統計） | 厚労省API | IPSS将来推計 |
| 土地利用・都市 | 国土数値情報 | 都市計画基礎調査 | G空間情報センター |
| 地価・不動産 | 不動産情報ライブラリ | e-Stat（地価公示） | 国交省土地総合情報 |
| 産業・経済 | RESAS | e-Stat（経済センサス） | 内閣府GDP |
| 雇用・賃金 | e-Stat（労働力調査） | 厚労省賃金統計API | OECD Labour |
| 環境・気候 | Google Earth Engine | 気象庁AMeDAS | 環境省GISデータ |
| 交通・人流 | 国交省PT調査 | V-RESAS（人流） | GTFS |
| 施設・POI | 国土数値情報 | OpenStreetMap | 川崎市GISデータ |
| 国際比較 | OECD Data | World Bank | UN Data |
| 行政財政 | 総務省地方財政状況 | 川崎市予算決算書 | e-Stat |
| 衛星・標高 | Google Earth Engine | 国土地理院 | NASA Earthdata |

---

## 1. 政府統計・行政データポータル

### e-Stat（政府統計の総合窓口）
- URL: https://www.e-stat.go.jp
- API登録: https://www.e-stat.go.jp/api/
- 主なデータ: 国勢調査・経済センサス・学校基本調査・建築着工統計・農業センサス 等

```python
import requests, pandas as pd

ESTAT_APP_ID = "YOUR_APP_ID"

def search_estat(keyword: str, limit: int = 20) -> pd.DataFrame:
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"
    res = requests.get(url, params={"appId": ESTAT_APP_ID, "searchWord": keyword, "limit": limit})
    tables = res.json()["GET_STATS_LIST"]["DATALIST_INF"]["TABLE_INF"]
    return pd.DataFrame([{"ID": t["@id"], "統計名": t["STAT_NAME"]["$"], "表題": t["TITLE"]["$"]} for t in tables])

def download_estat(stats_data_id: str, area_code: str = None) -> pd.DataFrame:
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
    params = {"appId": ESTAT_APP_ID, "statsDataId": stats_data_id, "metaGetFlg": "Y", "limit": 100000}
    if area_code:
        params["cdArea"] = area_code
    data = requests.get(url, params=params).json()["GET_STATS_DATA"]["STATISTICAL_DATA"]
    df = pd.DataFrame(data["DATA_INF"]["VALUE"])
    df["value"] = pd.to_numeric(df["$"], errors="coerce")
    return df

# よく使うstatsDataId（川崎市 area_code="14130"）
ESTAT_IDS = {
    "国勢調査_人口":         "0000010101",
    "住民基本台帳_人口移動":  "0000010030",
    "建築着工統計":           "0000010097",
    "学校基本調査":           "0000010101",
    "経済センサス_活動調査":  "0000010095",
}
```

### DATA.GO.JP（政府オープンデータポータル）
- URL: https://www.data.go.jp
- API: CKAN API（登録不要）

```python
def search_datagov(keyword: str, rows: int = 20) -> pd.DataFrame:
    url = "https://www.data.go.jp/api/3/action/package_search"
    res = requests.get(url, params={"q": keyword, "rows": rows})
    results = res.json()["result"]["results"]
    return pd.DataFrame([{
        "タイトル": r["title"],
        "組織": r.get("organization", {}).get("title", ""),
        "URL": r.get("url", ""),
        "形式": [rr.get("format","") for rr in r.get("resources", [])],
    } for r in results])

# 利用例
df = search_datagov("川崎市 保育所")
```

### RESAS（地域経済分析システム）
- URL: https://resas.go.jp
- API登録: https://opendata.resas-portal.go.jp
- 主なデータ: 人口ピラミッド・将来推計・産業構造・観光・農業・医療

```python
RESAS_KEY = "YOUR_RESAS_KEY"
RESAS_BASE = "https://opendata.resas-portal.go.jp/api/v1"
HEADERS = {"X-API-KEY": RESAS_KEY}

def resas_population(pref_code: int, city_code: str) -> pd.DataFrame:
    """人口構成（総人口・年少・生産年齢・老年）"""
    res = requests.get(f"{RESAS_BASE}/population/composition/perYear",
                       headers=HEADERS, params={"prefCode": pref_code, "cityCode": city_code})
    dfs = [pd.DataFrame(d["data"]).assign(区分=d["label"]) for d in res.json()["result"]["data"]]
    return pd.concat(dfs, ignore_index=True)

def resas_migration(pref_code: int, city_code: str, year: int = 2020) -> dict:
    """転入・転出・純移動"""
    res = requests.get(f"{RESAS_BASE}/population/migrateAnalysis/forFrom",
                       headers=HEADERS, params={"prefCode": pref_code, "cityCode": city_code, "year": year})
    return res.json()["result"]

def resas_industry(pref_code: int, city_code: str) -> pd.DataFrame:
    """産業別付加価値額"""
    res = requests.get(f"{RESAS_BASE}/industry/power/forArea",
                       headers=HEADERS, params={"prefCode": pref_code, "cityCode": city_code})
    return pd.DataFrame(res.json().get("result", {}).get("data", []))

# 利用例（川崎市：prefCode=14, cityCode="14130"）
df_pop = resas_population(14, "14130")
```

### V-RESAS（コロナ影響・人流・消費）
- URL: https://v-resas.go.jp
- 主なデータ: メッシュ人流・消費動向・雇用・飲食店

---

## 2. 国土・都市・インフラ系

### 国土数値情報（国交省）
- URL: https://nlftp.mlit.go.jp/ksj/
- 形式: GML(GeoJSON)/Shapefile
- 主なデータ: 用途地域・施設・河川・道路・公園・医療機関

```python
import geopandas as gpd
import requests, zipfile, io, os

def download_ksj_zip(url: str, save_dir: str = "data/raw/gis/") -> str:
    """国土数値情報ZIPをダウンロードして展開する"""
    os.makedirs(save_dir, exist_ok=True)
    res = requests.get(url, timeout=120)
    z = zipfile.ZipFile(io.BytesIO(res.content))
    z.extractall(save_dir)
    print(f"展開完了: {save_dir}")
    return save_dir

# よく使うデータとURL例（年度・地域によりURLが変わるため要確認）
KSJ_URLS = {
    "用途地域_神奈川": "https://nlftp.mlit.go.jp/ksj/gml/data/A29/A29-19/A29-19_14_GML.zip",
    "医療機関_全国":   "https://nlftp.mlit.go.jp/ksj/gml/data/P04/P04-21/P04-21_GML.zip",
    "公園_全国":       "https://nlftp.mlit.go.jp/ksj/gml/data/P13/P13-22/P13-22_GML.zip",
    "鉄道駅_全国":     "https://nlftp.mlit.go.jp/ksj/gml/data/N02/N02-22/N02-22_GML.zip",
}
```

### 不動産情報ライブラリ（国交省）
- URL: https://www.reinfolib.mlit.go.jp
- API登録: サイト上で申請
- 主なデータ: 不動産取引価格・地価公示・都市計画決定

```python
REINFOLIB_KEY = "YOUR_KEY"

def get_real_estate_prices(pref_code: int, year: int, quarter: int = 1) -> pd.DataFrame:
    """不動産取引価格を取得する（四半期単位）"""
    url = "https://www.reinfolib.mlit.go.jp/ex-api/external/XIT001"
    headers = {"Ocp-Apim-Subscription-Key": REINFOLIB_KEY}
    params = {"year": year, "quarter": quarter, "area": str(pref_code).zfill(2)}
    res = requests.get(url, headers=headers, params=params)
    return pd.DataFrame(res.json().get("data", []))

def get_land_price(pref_code: int, year: int) -> pd.DataFrame:
    """地価公示を取得する"""
    url = "https://www.reinfolib.mlit.go.jp/ex-api/external/XPT001"
    headers = {"Ocp-Apim-Subscription-Key": REINFOLIB_KEY}
    res = requests.get(url, headers=headers, params={"year": year, "area": str(pref_code).zfill(2)})
    return pd.DataFrame(res.json().get("data", []))
```

### G空間情報センター
- URL: https://www.geospatial.jp
- 形式: API / GeoJSON / Shapefile
- 主なデータ: 各種GISデータ横断ポータル

---

## 3. 自治体オープンデータ

| 自治体 | ポータルURL | API |
|---|---|---|
| 川崎市 | https://www.city.kawasaki.jp/opendata/ | 一部Socrata |
| 川崎市統計書 | https://www.city.kawasaki.jp/shisei/category/51-4-0-0-0-0-0-0-0-0.html | Excel/PDF |
| 横浜市 | https://data.city.yokohama.lg.jp | CKAN API |
| 東京都 | https://catalog.data.metro.tokyo.lg.jp | CKAN API |
| 神奈川県 | https://www.pref.kanagawa.jp/osirase/opendata/ | ❌ |

```python
def search_yokohama_opendata(keyword: str) -> pd.DataFrame:
    """横浜市オープンデータをCKAN APIで検索する"""
    url = "https://data.city.yokohama.lg.jp/api/3/action/package_search"
    res = requests.get(url, params={"q": keyword, "rows": 20})
    results = res.json()["result"]["results"]
    return pd.DataFrame([{"title": r["title"], "url": r.get("url","")} for r in results])
```

---

## 4. 環境・気候・衛星データ

### Google Earth Engine（Python API）
- 登録: https://earthengine.google.com
- 主なデータ: Sentinel-2（植生・土地被覆）・Landsat 8/9（地表面温度）・MODIS（広域）

```python
import ee
ee.Authenticate()
ee.Initialize(project="YOUR_PROJECT")

# Sentinel-2 NDVI（川崎市範囲）
kawasaki_bbox = ee.Geometry.BBox(139.45, 35.47, 139.65, 35.63)

def get_ndvi(year: int, month_start: int = 6, month_end: int = 8) -> ee.Image:
    """指定年の夏季平均NDVIを返す"""
    collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                  .filterBounds(kawasaki_bbox)
                  .filterDate(f"{year}-{month_start:02d}-01", f"{year}-{month_end:02d}-30")
                  .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
                  .map(lambda img: img.normalizedDifference(["B8","B4"]).rename("NDVI")))
    return collection.mean()

# Landsat 地表面温度
def get_lst(year: int) -> ee.Image:
    """指定年の夏季平均地表面温度（LST）を返す"""
    collection = (ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
                  .filterBounds(kawasaki_bbox)
                  .filterDate(f"{year}-06-01", f"{year}-09-30")
                  .map(lambda img: img.select("ST_B10").multiply(0.00341802).add(149.0 - 273.15).rename("LST_C")))
    return collection.mean()
```

### 気象庁 AMeDAS
- URL: https://www.data.jma.go.jp/obd/stats/etrn/

```python
def download_amedas(station_no: str, year: int, month: int) -> pd.DataFrame:
    """AMeDASの月別データをスクレイピングで取得する（公式APIなし）"""
    url = (f"https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php"
           f"?prec_no=46&block_no={station_no}&year={year}&month={month}&day=&view=")
    df = pd.read_html(url, header=[0,1])[0]
    return df

# 川崎（アメダス川崎局の番号は要確認）
# df_weather = download_amedas("47670", 2023, 7)
```

---

## 5. 施設・POI・地理情報

### OpenStreetMap（Overpass API）
- 登録不要・無料

```python
def get_osm_facilities(lat: float, lon: float,
                       radius_m: int = 3000,
                       amenity: str = "school") -> pd.DataFrame:
    """
    指定座標の周辺施設をOSMから取得する
    amenity: school / kindergarten / hospital / clinic /
             pharmacy / supermarket / park / bus_station
    """
    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="{amenity}"](around:{radius_m},{lat},{lon});
      way["amenity"="{amenity}"](around:{radius_m},{lat},{lon});
    );
    out center;
    """
    res = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
    elements = res.json().get("elements", [])
    rows = []
    for e in elements:
        center = e.get("center", e)
        rows.append({
            "name":    e.get("tags", {}).get("name", "不明"),
            "lat":     center.get("lat"),
            "lon":     center.get("lon"),
            "amenity": amenity,
            "osm_id":  e["id"],
        })
    df = pd.DataFrame(rows)
    print(f"[OSM] {amenity}：{len(df)}件（半径{radius_m}m）")
    return df

# 利用例（川崎市役所周辺 3km の保育所）
df_nursery = get_osm_facilities(35.5308, 139.7028, 3000, "kindergarten")
```

### 国土地理院 標高・地形API

```python
def get_elevation(lat: float, lon: float) -> float:
    """指定座標の標高（m）を取得する"""
    url = "https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php"
    res = requests.get(url, params={"lon": lon, "lat": lat, "outtype": "JSON"})
    return res.json().get("elevation")

def get_gsi_tiles_url(z: int, x: int, y: int, layer: str = "std") -> str:
    """国土地理院タイルURLを返す（地図・写真・標高）
    layer: std（標準地図）/ seamlessphoto（空中写真）/ relief（色別標高）
    """
    return f"https://cyberjapandata.gsi.go.jp/xyz/{layer}/{z}/{x}/{y}.png"
```

---

## 6. 社会・経済・国際比較

### IPSS（国立社会保障・人口問題研究所）
- URL: https://www.ipss.go.jp
- 主なデータ: 都道府県別将来人口推計・世帯数推計
- 形式: Excel/CSV（API なし）
- 直接DL: https://www.ipss.go.jp/pp-pref/j/

### 総務省 地方財政状況調査
- URL: https://www.soumu.go.jp/iken/zaisei.html
- 主なデータ: 財政力指数・経常収支比率・実質公債費比率
- 形式: Excel（API なし）

### 厚労省 API（賃金・雇用・医療）

```python
def search_mhlw_stat(keyword: str) -> pd.DataFrame:
    """厚生労働省統計情報をe-Stat経由で検索（省庁コード=00450）"""
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"
    params = {"appId": ESTAT_APP_ID, "searchWord": keyword, "statsCode": "00450"}
    res = requests.get(url, params=params)
    tables = res.json()["GET_STATS_LIST"]["DATALIST_INF"]["TABLE_INF"]
    return pd.DataFrame([{"ID": t["@id"], "表題": t["TITLE"]["$"]} for t in tables])
```

### OECD Data API（国際比較）
- URL: https://data.oecd.org / https://stats.oecd.org

```python
def get_oecd_csv(dataset: str, filter_expr: str = "JPN") -> pd.DataFrame:
    """OECD SDMX-JSON API からCSVで取得する
    dataset 例: REGION_DEMOGR / HH_DASH / CITIES / EAG_POP
    filter_expr: 国コード（JPN=日本）や指標コード
    """
    url = f"https://stats.oecd.org/SDMX-JSON/data/{dataset}/{filter_expr}/all"
    res = requests.get(url, params={"contentType": "csv"})
    from io import StringIO
    return pd.read_csv(StringIO(res.text))

# 利用例
# df_oecd = get_oecd_csv("REGION_DEMOGR", "JPN")
```

### World Bank Open Data

```python
def get_worldbank(indicator: str, country: str = "JP",
                  start: int = 2000, end: int = 2023) -> pd.DataFrame:
    """World Bank API からデータを取得する
    indicator 例: SP.POP.TOTL（人口）/ EN.URB.LCTY（都市人口）/ NY.GDP.PCAP.CD（一人当たりGDP）
    """
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {"date": f"{start}:{end}", "format": "json", "per_page": 500}
    res = requests.get(url, params=params)
    data = res.json()[1]
    return pd.DataFrame([{"year": d["date"], "value": d["value"], "country": d["country"]["value"]}
                         for d in data if d["value"] is not None])

# 利用例
# df_wb = get_worldbank("SP.URB.TOTL.IN.ZS")  # 都市人口比率
```

---

## 主要地域コード（川崎市・近隣）

| 地域 | 都道府県コード | 市区町村コード | RESAS prefCode | RESAS cityCode |
|---|---|---|---|---|
| 神奈川県 | 14 | - | 14 | - |
| 川崎市 | 14 | 14130 | 14 | 14130 |
| 川崎区 | 14 | 14131 | 14 | 14131 |
| 幸区 | 14 | 14132 | 14 | 14132 |
| 中原区 | 14 | 14133 | 14 | 14133 |
| 高津区 | 14 | 14134 | 14 | 14134 |
| 多摩区 | 14 | 14135 | 14 | 14135 |
| 宮前区 | 14 | 14136 | 14 | 14136 |
| 麻生区 | 14 | 14137 | 14 | 14137 |
| 横浜市 | 14 | 14100 | 14 | 14100 |
| 東京都 | 13 | - | 13 | - |
