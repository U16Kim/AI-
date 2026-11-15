#!/usr/bin/env python3
"""スライドの「上品さ」の監査。作った後に必ず実行する。

使い方:  python3 audit.py deck.pptx --dark 1,8,12        （--dark は全面濃色の頁番号）
          python3 audit.py deck.pptx --dark 1 --paper       （地が紙色 F4F6FA の資料。既定は白）
合格の目安: 尺度外のサイズ なし／10.5pt未満 なし／コントラスト不足 なし／
            太字の比率 40%以下／サイズの種類 13以内／最大÷本文(14) 13.3以下／全面濃色 3枚以内
"""
import sys, collections
from pptx import Presentation

SCALE = [10.5, 12, 14, 17, 21, 25, 30, 36, 43, 62, 89, 107, 185]   # references/design-system.md と同じ
NIGHT, PAPER, WHITE = "0B1730", "F4F6FA", "FFFFFF"
IN = 914400


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def fill_hex(sh):
    try:
        if sh.fill.type == 1:
            return str(sh.fill.fore_color.rgb)
    except Exception:
        pass
    return None


def main(path, dark, paper):
    prs = Presentation(path)
    sizes = collections.Counter(); off = collections.Counter()
    bold = total = 0; low = []; bad = []; edges_n = {}
    for n, s in enumerate(prs.slides, 1):
        bg = NIGHT if n in dark else (PAPER if paper else WHITE)
        shapes = list(s.shapes); edges = set()
        for i, sh in enumerate(shapes):
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            cx = (sh.left + sh.width / 2) / IN; cy = (sh.top + sh.height / 2) / IN
            under = fill_hex(sh)
            if not under:                                  # 文字の下にある、いちばん手前の塗りを背景とみなす
                for k in range(i - 1, -1, -1):
                    o = shapes[k]; h = fill_hex(o)
                    if h and o.left / IN <= cx <= (o.left + o.width) / IN and o.top / IN <= cy <= (o.top + o.height) / IN:
                        under = h; break
                under = under or bg
            edges.add(round(sh.left / IN / 0.05) * 0.05)
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    t = r.text.strip()
                    if not t or not r.font.size:
                        continue
                    sz = r.font.size.pt
                    sizes[sz] += len(t); total += 1; bold += 1 if r.font.bold else 0
                    if sz < 10.5: low.append((n, sz, t[:12]))
                    if sz not in SCALE: off[sz] += 1
                    try:
                        col = str(r.font.color.rgb); ratio = contrast(col, under)
                        if ratio < (3.0 if sz >= 24 else 4.5):
                            bad.append((n, round(ratio, 2), col, under, t[:10]))
                    except Exception:
                        pass
        edges_n[n] = len(edges)
    print("サイズ(pt:文字数):", sorted(sizes.items()))
    print("尺度外のサイズ:", dict(off) or "なし", "／サイズの種類:", len(sizes))
    print("太字の比率（文字のまとまりの数）: %.0f%%" % (100 * bold / max(total, 1)))
    print("10.5pt未満:", low or "なし")
    print("コントラスト不足:", bad or "なし")
    print("最大÷本文(14): %.1f" % (max(sizes) / 14 if sizes else 0))
    print("全面濃色の枚数:", len(dark))
    print("頁ごとの左端の種類数:", edges_n)
    print("注意: 表（addTable）の中の文字と、プレースホルダの既定サイズは、この監査の対象外。")


if __name__ == "__main__":
    a = sys.argv
    d = {int(x) for x in a[a.index("--dark") + 1].split(",")} if "--dark" in a else set()
    main(a[1], d, "--paper" in a)
