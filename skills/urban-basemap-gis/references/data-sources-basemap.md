# ベースマップ用データ源：確認結果と未確認事項

確認日：2026-11-09。確認できたものは出典を付け、確認できなかったものは「⚠️未確認」と明記する。

## 1. 行政区域：国土数値情報「行政区域データ（N03）」

| 項目 | 内容 | 出典 |
|---|---|---|
| 配布ページ | https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html | 配布ページ（確認済み） |
| 最新版 | 2026年（令和8年）版、基準日 2026-01-01（2026年4月更新） | 同上 |
| ファイル名 | 全国：`N03-20260101_GML.zip`／都道府県別：`N03-20260101_{都道府県コード2桁}_GML.zip`（例：北海道 `_01_`、神奈川 `_14_`）。地方ブロック版もあり（関東 `_53`） | 同上 |
| 形式 | GML（JPGIS2014準拠）・Shapefile・GeoJSON | 同上 |
| ライセンス | オープンデータ（CC BY 4.0）。原典表示あり（文言は取得ページの記載に従う） | 同上 |
| 属性 | N03_001 都道府県名／N03_002 振興局名／N03_003 郡・政令指定都市名／N03_004 市区町村名（政令市は区名）／N03_007 行政区域（全国地方公共団体）コード5桁 | 製品仕様書 v4.1、解説記事で確認（N03_005・006 は未確認） |
| 座標系 | JGD2011（経緯度） | 製品仕様書 v4.1 https://nlftp.mlit.go.jp/ksj/gml/product_spec/KS-PS-N03-v4_1.pdf |
| ⚠️未確認 | ①直接ダウンロードURLの形式（ページにはファイル名のみ表示）→ `download_n03()` は推定URL。失敗時は手動 ②zip内のファイル構成（Shapefile／GeoJSONの有無）は版により異なる可能性 ③製品仕様書は表紙が v4.1（2026年3月）、本文に v4.0 の記載が混在していた | |

**使うときの注意**
- 同じ自治体が複数ポリゴン（飛び地・島）になっている → `dissolve_admin` で1行にまとめる。
- 「所属未定地」などコードが空の行は、`read_n03` が除外して件数を表示する（面積の合計がずれる原因になるため、除外件数を記録する）。
- 年次を変えると自治体の境界・コードが変わる（合併・区の新設等）。**統計の年と行政区域の年を揃える**。

## 2. OpenStreetMap

| 項目 | 内容 | 出典 |
|---|---|---|
| ライセンス | ODbL。「© OpenStreetMap contributors」の表記が必要 | OSM の標準的な利用条件（⚠️個別の最新条文は未確認） |
| Overpass 公開サーバーの方針 | 1日1万クエリ未満・1GB未満・処理10分以内なら一回限りの利用として許容。定期利用は100分の1（1日100クエリ・10MB）が目安。並列実行禁止。429/406 は30秒待つ。`User-Agent` で自己申告。キャッシュする。商用は自前/有償サーバー | OSM Wiki「Overpass API」 https://wiki.openstreetmap.org/wiki/Overpass_API |
| 既定のタイムアウト | 3分（クエリで延長可） | 同上 |
| 取得ライブラリ | OSMnx（`features_from_polygon`・`graph_from_polygon`）。サンドボックスで v2.1.1 の動作を確認 | 動作確認 |
| ⚠️未確認 | 現在の公開サーバーの混雑状況・実際の応答時間（Claudeの環境からは接続できず未検証） | |

### OSMタグの設計（`OSM_LAYERS`）
| レイヤー | 取得するタグ | 形 | 備考 |
|---|---|---|---|
| roads | 道路ネットワーク（OSMnx `drive`） | 線 | 高速・幹線・生活道路。`highway` で太さを変えて描く |
| rail | `railway=rail/subway/light_rail/tram/monorail` | 線 | |
| stations | `railway=station` | 点 | 面で描かれた駅は代表点に変換 |
| water / waterways | `natural=water`・`waterway=riverbank`／`waterway=river/canal/stream` | 面／線 | 海の扱い（`natural=coastline`）は含めていない。東京湾岸の図では海が空白になる |
| parks | `leisure=park/garden/playground/pitch` | 面 | |
| buildings | `building=*` | 面 | 非常に重い |
| schools / childcare / hospitals / supermarkets | `amenity=school`／`kindergarten, childcare`／`hospital, clinic`／`shop=supermarket` | 点 | **網羅性は地域により異なる**。施設数の集計に使う前に公式データと照合する |

> 日本の保育所のタグ付けは `amenity=kindergarten` と `amenity=childcare` が混在する可能性がある（⚠️未確認）。件数が公式統計より極端に少ない場合は、タグの違いか未入力を疑う。

## 3. 背景地図タイル（任意）
- 国土地理院タイル 標準地図：`https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png`（OSM Wiki「JA:GSImaps」で確認）。
- 淡色地図（pale）は `…/xyz/pale/{z}/{x}/{y}.png` の形式と思われるが、**⚠️未確認**。国土地理院の「地理院タイル一覧」（https://maps.gsi.go.jp/development/ichiran.html ⚠️URL・内容は今回未確認）で確認する。
- 出典表示・利用条件は国土地理院の利用規約に従う（⚠️要確認）。**OSMのタイルサーバーを、大量・業務用途で直接叩かない**（利用方針の制限があるため。コードもタイルに依存せず、ベクターデータを自分で描く方式にしてある）。

## 4. 座標系
- 保存・受け渡し：WGS84（EPSG:4326）。QGIS・Tableau・GeoJSON はこれが無難。
- 面積・距離・縮尺バー：投影座標系（m単位）。首都圏（東京都・神奈川県・埼玉県・千葉県）は平面直角座標系Ⅸ系＝EPSG:6677（pyproj で名称「JGD2011 / Japan Plane Rectangular CS IX」を確認）。
- ⚠️ 上記4都県が全域Ⅸ系かは、国土地理院の平面直角座標系の区域区分表で確認すること（島しょ部・一部地域は別の系）。他県は系が異なるため `pick_local_crs` は UTM を推定する。

## 5. 自治体コード
- 総務省「全国地方公共団体コード」は6桁（末尾は検査数字）。結合には先頭5桁を使う。
- 川崎市の区コード：川崎区14131・幸区14132・中原区14133・高津区14134・多摩区14135・宮前区14136・麻生区14137。川崎市14130、横浜市14100。
- 政令市の「市」コードは区コードから規則で導けない（横浜市14100の区は 14101〜14118）。コードは `DESIGNATED_CITY_CODES` の表で補う（⚠️20市・2026年時点の想定。新設・変更は総務省の一覧で確認）。
