# PPTXの部品と実装上の注意（pptxgenjs）

`scripts/lib.js` を作業フォルダにコピーし、`require` して使う。全ての部品を使った試作を描画し、`audit.py`（尺度外なし・コントラスト不足なし）と pptx スキルの `validate.py` を通してある（確認日 2026-11-15。描画は LibreOffice）。設計値は `design-system.md`。

## 1. 準備と使い方

```bash
# 誰が：作成者（Claude）が／どこで：作業フォルダで／何を：部品を使える状態にする
npm install pptxgenjs
cp <このスキル>/scripts/lib.js <このスキル>/scripts/audit.py .
```

```js
const L = require("./lib.js"); const { P, MX, CT, CB, CW, T, box } = L;
const pres = L.newDeck("件名");                       // 白地。投影が主なら L.newDeck("件名", { paper: true })

let s = L.dark(pres);                                  // 全面濃色（表紙・山場・Ask。3枚まで）
L.hero(s, "R9", { x: MX, y: 1.4, w: 6, h: 2.9, fontSize: 185, num: true, color: "FFFFFF" });
L.plate(pres, s, MX, 5.7, "12月中旬まで", true);        // 期限札（濃色面）

s = L.frame(pres, "施策体系　2", "施策は3本の柱で構成し、柱ごとに事業と成果指標を結ぶ", "出典：○○（令和8年）");
L.tree(pres, s, { purpose: "目的の文", pillars: [{ no: "1", name: "柱の名", projects: ["事業A", "事業B"], kpi: "指標\n現状→目標（目標）" }] });

s = L.frame(pres, "施策フロー　3", "…", "出典：…");
L.swimlane(pres, s, { phases: ["相談", "申請"], lanes: ["民間事業者", "市"],
  tasks: [{ lane: 0, phase: 0, text: "企画を相談する" }, { lane: 1, phase: 1, text: "審査する", key: true }], links: [[0, 1]] });
s.addNotes("台本…");
pres.writeFile({ fileName: "out.pptx" });
```

コードの意味：`newDeck` が、タイトルの位置と大きさをそろえた台紙を作る。`frame` は「章名・結論のタイトル・出典」が入った1頁を返し、その上に `tree`（体系図）や `swimlane`（主体ごとの流れ）などの部品を置く。`key: true` を付けた箱は、関門として朱で強調される。`addNotes` は、話す内容の台本を頁に付ける。

## 2. 部品の一覧

| 部品 | 作るもの | 渡すもの | 読みやすい範囲 |
|---|---|---|---|
| `newDeck(title, {paper})` | 台紙（白地／紙色） | — | — |
| `frame(pres, 章名, タイトル, 出典)` | 標準の1頁 | タイトルは結論の文 | タイトルは2行以内 |
| `dark(pres)` | 全面濃色の頁 | — | 1資料に3枚まで |
| `hero(s, 文字, {x,y,w,h,fontSize,num,color})` | 主役の大字 | `num:true` で数字・欧文の書体 | 62〜185pt |
| `tree(pres, s, {purpose, pillars})` | 施策体系図 | 柱ごとに `no,name,projects,kpi` | 柱2〜4本、事業は柱ごとに3つまで |
| `swimlane(pres, s, {phases, lanes, tasks, links})` | 主体×段階の流れ | `key:true` で関門 | 主体2〜4、段階3〜6 |
| `flow(pres, s, steps)` | 番号付きの手順 | `h`（動詞で始める）、`b`、`who` | 3〜5段 |
| `roadmap(pres, s, {periods, rows})` | 工程表 | `gate:true` で関門、`plan:true` で未確定（破線） | 行は8本まで |
| `options(pres, s, {criteria, options})` | 選択肢の比較表 | `rec:true` で推奨 | 案は2〜4、軸は4〜6 |
| `plate(pres, s, x, y, 文字, 濃色面か)` | 期限札 | 全頁で同じ語 | 幅3.1インチ |
| `tag(pres, s, x, y, w, 文字, 確定か)` | 確定／未確定の札 | — | — |
| `numline(s, x, 下端y, parts)` | 数字＋単位 | `[{t:"45",fs:107,num:true},{t:"日",fs:30}]` | — |
| `box`・`arrow`・`elbow`・`badge`・`T` | 自由な図の基本部品 | — | 図の要素は9個以内 |

- 範囲を超えるなら、頁を分けるか、上位の概念でまとめる。
- 表紙・サマリー・Askは `box` と `T` で組む（サマリーは、左に濃色のAskのパネル、右に番号付きの要点3つが定石）。
- 部品にない図（事業スキーム図、路線図、判断フロー）は `box`・`badge`・`arrow` を組み合わせる。矢印に説明を付けるときは、`T` を矢印の中点に置く。
- チャートは `addChart` で作る（画像にしない）。`valAxisMinVal: 0` を入れ、軸・凡例・データラベルの体裁を全チャートでそろえる。形と色の決め方は `dataviz`。
- 図は図形で作り、画像にしない。受け取った人が自分で直せるようにするため。

## 3. pptxgenjs の地雷（全て実際に踏んだもの）

- 色に `#` を付けない。8桁の色を使わない（ファイルが壊れる）。透明度は `transparency` で指定する。
- `pres.layout = "LAYOUT_WIDE"` は、`addSlide` より前に設定する。
- `valAxisMinVal: 0` を全チャートに入れる。入れないと、軸が負の値まで伸びる。
- 積み上げ棒の `dataLabelPosition` に `outEnd` を使わない（ファイルが壊れる）。
- オプションのオブジェクトは、呼び出すたびに新しく作る（pptxgenjs が中身を書き換える）。
- 影の `offset` は0以上。`rectRadius` は角丸の四角形にだけ効く。
- 絵文字を使わない（環境によって表示されない）。
- 書き出したファイルにフォルダの項目が混ざり、クラウド上で開けないことがある。`validate.py` が注意を出したら、`zip -dq out.pptx '*/'` で取り除く。

## 4. 描画と実機の差

- 確認用の描画（LibreOffice）には Meiryo・游明朝・Cambria がなく、代わりの書体で幅がずれる。主役の欧文・数字は幅に15%の余裕を持たせ、日本語の長文は `\n` で句の切れ目に改行する。
- 「0 円」のような和欧のすき間は LibreOffice だけの現象で、PowerPoint には出ない。数字と単位は `numline` で別の箱に置く。
- 縦書きは、LibreOffice で後続の文字に重なる。使わない。
- **最終の見た目は、PowerPoint の実機で確認するよう依頼者に伝える。** こちらの描画で確認できるのは、はみ出し・重なり・配置までである。

## 5. 監査

```bash
python3 audit.py out.pptx --dark 1,8,12      # --dark は全面濃色の頁番号。紙色の地なら --paper を付ける
```

| 項目 | 合格の目安 |
|---|---|
| 尺度外のサイズ | なし |
| サイズの種類 | 13以内 |
| 10.5pt未満 | なし |
| コントラスト不足 | なし |
| 太字の比率（文字のまとまりの数） | 40%以下 |
| 最大÷本文(14) | 13.3以下 |
| 全面濃色の枚数 | 3以内（付録の扉を置く場合は4） |

外れた項目は、直してから見せる。表（`addTable`）の中の文字は監査の対象外なので、目で確かめる。
