"""国土数値情報から、立適ヘルスチェックに使うデータを取得する。

使い方:  python src/01_download.py 41   (引数は都道府県コード。佐賀県=41)
出力:   data_raw/<データ名>/ に展開、data_raw/manifest.csv に出典と取得日時を記録
"""
import csv
import datetime as dt
import hashlib
import os
import sys
import zipfile
from pathlib import Path

import requests

BASE = "https://nlftp.mlit.go.jp/ksj/gml/data"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data_raw"


def datasets(pref: str, mesh1: list[str]) -> list[tuple[str, str, str]]:
    """(名前, パス, 説明) の一覧。ファイル名は国土数値情報の一覧ページで確認済みのもの。"""
    items = [
        ("A50", f"A50/A50-20/A50-20_{pref}_GML.zip", "立地適正化計画区域(2020年12月31日時点)"),
        ("P04", f"P04/P04-20/P04-20_{pref}_GML.zip", "医療機関(2020年)"),
        ("P14", f"P14/P14-23/P14-23_{pref}_GML.zip", "福祉施設(2023年)"),
        ("P11", f"P11/P11-22/P11-22_{pref}_SHP.zip", "バス停留所(2022年)"),
        ("A29", f"A29/A29-19/A29-19_{pref}_GML.zip", "用途地域(2019年)"),
        ("A33", f"A33/A33-25/A33-25_{pref}_GEOJSON.zip", "土砂災害警戒区域(2025年)"),
        ("M500", f"m500r6/m500r6-24/500m_mesh_2024_{pref}_GEOJSON.zip", "500mメッシュ別将来推計人口(R6国政局推計)"),
        ("N03", f"N03/N03-2025/N03-20250101_{pref}_GML.zip", "行政区域(2025年1月1日)"),
    ]
    for m in mesh1:  # 洪水浸水想定区域は1次メッシュ単位。ファイル名の10/20は区分コード(河川管理者の区分と推定。未確認)。
        # 各ファイルの中に「計画規模」「想定最大規模」などのカテゴリが入っているため、両方を取得して合成する。
        for kind in ("10", "20"):
            items.append((f"A31b_{kind}_{m}", f"A31b/A31b-25/A31b-25_{kind}_{m}_GEOJSON.zip", f"洪水浸水想定区域 区分{kind} 1次メッシュ{m}"))
    return items


def main() -> None:
    pref = sys.argv[1] if len(sys.argv) > 1 else "41"
    mesh1 = sys.argv[2].split(",") if len(sys.argv) > 2 else ["5030"]
    RAW.mkdir(exist_ok=True)
    verify = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
    if not Path(verify).exists():
        verify = True  # 既定の証明書を使う。検証は無効化しない。
    rows = []
    for name, path, desc in datasets(pref, mesh1):
        url = f"{BASE}/{path}"
        dest_zip = RAW / Path(path).name
        out_dir = RAW / dest_zip.stem
        if not dest_zip.exists():
            r = requests.get(url, timeout=180, verify=verify)
            if r.status_code != 200:
                print(f"SKIP {name}: HTTP {r.status_code} {url}")
                rows.append([name, desc, url, r.status_code, "", "", ""])
                continue
            dest_zip.write_bytes(r.content)
        data = dest_zip.read_bytes()
        with zipfile.ZipFile(dest_zip) as z:
            z.extractall(out_dir)
        print(f"OK   {name:14s} {len(data)/1e6:6.2f}MB  {desc}")
        rows.append([name, desc, url, 200, len(data), hashlib.sha256(data).hexdigest()[:16],
                     dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")])
    with open(RAW / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "description", "url", "http", "bytes", "sha256_16", "fetched_utc"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
