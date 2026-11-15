---
name: "kmr-visual-deliverables"
description: "資料・スライド・ビジュアル成果物の作成基準（型の判定、デザイン3案、政策説明スライド、高密度ビジュアル、検証済みのレイアウト部品）。「資料を作って」「スライドにして」「PPTX／HTML／Word／PDFで」「市長・局長・幹部への説明資料」「講演・登壇用のスライド」「見やすくして」「デザインを考えて」「かっこよくしたい」等、見た目を伴う成果物を作る・直す依頼では必ず使う。作る前の論理の骨格は logic-storyline、説明の中身（想定問答・台本）は exec-council-stakeholder-comms、提出前の検証は deliverable-verifier。"
---

# 資料作成スキル（統合版）

木村雄一郎さん（川崎市・課長／まちづくり・政策企画）向けの成果物の作成基準。旧 `design-fit`（型の判定とデザイン導出）を統合済み。

**構成**：【共通】手順・禁止事項 → 【型B・C・D】政策説明スライド（幹部向け）→ 【型A・F・E】高密度ビジュアル基準（既存の§0〜§8）。

| 関連スキル | 役割 |
|---|---|
| logic-storyline | **作る前の設計図**（Ask・問い・結論・根拠3つ・反論への備え・見出しの通読テスト） |
| exec-council-stakeholder-comms | 幹部説明・答弁の**中身**（構成・想定問答・台本） |
| pptx | PPTXの技術仕様（pptxgenjsの地雷・検証スクリプト） |
| deliverable-verifier | 提出前の事実・数値・論理の検証 |
| kawasaki-admin-reference / metro-gov-reference | 川崎市／東京都・横浜市の確認済み事実・URL |
| dataviz | グラフの形・色・軸の決め方 |
| urban-development-practice / data-science-foundations / japan-law-research | 中身の専門的な裏付け（制度・事業性／分析／法令・判例） |

**大原則：デザインは「前回の見た目」ではなく「今回の内容・読み手・使われる場面」から毎回導く。** 題材と表現を混同しない（AIの話だから回路柄、量子の話だから星雲、都市の話だから俯瞰写真、は思考放棄）。

---

# 【共通】最初の手順と禁止事項

## 手順（この順に行う）

1. **型を判定する**（下表）。複数なら主たる型を選ぶ。
2. **読み手・部屋・立場を具体化する**：誰が（市長／局長／議会／市民）、どこで（会議室のプロジェクタ／手元で印刷／スマホ）、その場で何をするか（聞く／議論する／決裁する／持ち帰る）。こちらが「お願いする側」か「魅せる側」か「説明責任を負う側」か。
3. **一次情報を先に集める**（リサーチが先、書式は後）。数値は出典と時点を控える。
4. **ストーリーラインを文章で先に作る**（`logic-storyline` の設計図＝場面・問い・結論・ピラミッド・反論・構成案・30秒版。スライド特有の組み方は【型B・C・D】の「1. ストーリー設計」）。スライドを作り始めない。設計図が既に会話で確定していれば、それを使う。
5. **デザイン3案を1〜2行ずつ言語化して提示**し、推奨案で進める（「3.5 デザイン3案」参照）。理由を言えないデザインは、内容から導けていない証拠。重要案件は表紙＋施策体系図の2枚だけ3案で試作してよい。
6. **作る → 検証する**（既存§6の品質保証と、後述の自己点検）。

不足情報はまとめて1回だけ聞く（最大3項目：決めてほしいこと／持ち時間／印刷か投影か）。会話で確定済みなら聞かない。

## 型の判定

| 型 | 目的 | 読み手の行動 | 基調 | 画像 | 主役 |
|---|---|---|---|---|---|
| **A ビジョン・説得** | 心を動かす | 「やろう」と思う | 暗色可・余白大 | 象徴的ビジュアル有効 | コピー（言葉） |
| **B 意思決定・判断** | 選ばせる・承認させる | 決裁する | 白 | ほぼ不要 | 比較表・体系図・スコア |
| **C 実務協議・依頼** | 認識を揃え宿題を依頼 | 持ち帰って動く | 白・文書的 | **原則ゼロ** | 工程表・フロー・依頼リスト |
| **D 報告・記録** | 正確に伝える | 読み返す | 白 | データ図表のみ | 見出し階層と図表 |
| **E 技術・分析解説** | 理解させる | わかる | 白 | 概念図（説明用） | 図解 |
| **F 祝祭・広報・集客** | 高揚させる | 来場・拡散 | 自由 | 主役 | ビジュアル |
| **G 危機対応・謝罪** | 信頼を保つ | 安心する | 白・無彩色 | ゼロ | 事実と時系列（赤は使わない） |

- **市長・社長・幹部への政策説明は、原則 B（決裁）または C（協議）。【型B・C・D】を適用する。**
- 印刷・回覧される資料は**白基調が絶対**（暗背景はトナーを食い、書き込めず、コピーで潰れる）。
- お願いする側・説明責任を負う側が華美な演出をすると、中身の薄さの糊塗に見える。**抑制が誠実さの表現**になる。
- **型A・F・E は、後述の【型A・F・E】高密度ビジュアル基準も満たす。型B・C・D・G には生成画像の「枚数の要件」を適用しない**（装飾画像は不誠実に映る）。型B・Cでは、表紙・章扉も含めて画像を作らず、色面と活字で作る（§4.5）。
- ブランドは「要素の一貫性」（ロゴ・差し色・フッタ文言・用語）で担保し、同じ見た目にする必要はない。実務文書ではブランド色を強調（関門・Ask）に降格させる。

## 禁止事項

- 前回の資料の見た目の流用／題材＝表現の短絡／内容と無関係な装飾画像／暗背景＋グローを汎用の「高級感」にすること（型B・Cでは、表紙・章扉も画像を使わず、色面と活字で作る。§4.5）
- 情報密度が必要な表を余白優先で読みにくくすること（逆に、感情に訴える場面で表を並べることも誤り）
- 絵文字（環境依存で豆腐化する）／影・グラデーション／タイトル下の線／スライド端の色帯・縦ストライプ（AI生成物の典型で安っぽい）
- 箇条書きの羅列だけのスライド。必ず図・表・大型数字のいずれかを置く

---

# 【型B・C・D】政策説明スライド（市長・社長・幹部向けの中核）

## 1. ストーリー設計（スライド化の前に文章で）

1. **ゴールを1文で決める**：「（誰）に（何）を（決裁／了承／方針決定／情報共有）してほしい」。これが **Ask**。
2. **ピラミッドで組む**：結論（Ask）→ 根拠3つ以内 → 各根拠の裏付け（データ・事例・図）。
3. **スライドタイトルは「結論の文」にする**（例：「手続を一本化し、最短10日で実施できる体制にする」）。「現状と課題」「施策の概要」のような**名詞だけのタイトルは禁止**。全タイトルを順に読むだけで話が通ること（タイトル通読テスト）。1〜2行、全角40字以内。
4. **1スライド＝1メッセージ**。2つ言いたければ2枚にする。
5. **選択肢に「やらない」「延期」を入れる**。推奨案は1つ、理由は3つ以内。
6. **主張 → 図表 → 留保**の順。「ただし、こう読むべき」を1行添える。推計・目標値は「実績ではない」と明記。
7. **事例を必ず入れる**（国内外1〜3件、成功と失敗の両方）。川崎市の事実は `kawasaki-admin-reference` の確認済みのものを使う。

**標準構成**（持ち時間 ÷ 1.5〜2分 ＝ 本編の枚数。詳細は参考資料へ）

| 順 | スライド | 役割 |
|---|---|---|
| 1 | 表紙 | 件名・日付・所属 |
| 2 | **サマリー（結論＋Ask）** | 30秒で全体と依頼事項が伝わる |
| 3 | 現状と課題 | データ1〜2点＋「だから何か」（So-what）1行 |
| 4 | 基本方針・目的 | 何を目指すか |
| 5 | **施策体系図** | 目的→施策の柱→事業→指標 |
| 6 | **施策フロー** | 誰が・いつ・何をするか |
| 7 | 選択肢の比較 | 2〜3案＋やらない案、推奨を明示 |
| 8 | 効果・KPI／財政影響 | 数字を大きく |
| 9 | リスクと対応 | 上位3つ |
| 10 | **スケジュール** | 関門（決裁・議会・予算）を強調 |
| 11 | 体制・役割分担 | 主体×役割 |
| 12 | **Ask・次のステップ** | 決めてほしいこと／期限／持ち帰り事項 |

説明は30秒版（結論とAsk）・3分版（要点）・10分版（詳細）の3種を用意し、各スライドの `addNotes()` に台本を入れる。想定問答（財政・議会・関係局から出る質問）は別紙で用意する（中身は `exec-council-stakeholder-comms`）。

## 2. 施策の構造を伝える図の選び方

| 伝えたいこと | 使う図 | 部品（§7） |
|---|---|---|
| 施策の全体像・なぜこの事業か | **施策体系図**（目的→施策の柱→事業→成果指標） | `tree` |
| 誰がいつ何をするか／事務の流れ | **スイムレーン**（主体×フェーズ） | `swimlane` |
| 段階的な進め方 | **ステップ・フロー**（番号＋担当） | `flow` |
| 因果・効果の筋道（EBPM） | **ロジックモデル**（投入→活動→産出→短期成果→長期成果） | `flow`/`tree` を5列に |
| 官民の役割・お金・サービスの流れ | **事業スキーム図**（主体を箱、矢印に「何が動くか」） | `box`+`arrow` |
| 案の選択 | **比較表**（評価軸×案、推奨を色で） | `options` |
| 時間・関門 | **ロードマップ**（ガント＋関門を強調色） | `roadmap` |
| 役割分担 | **役割表**（主体×役割×期限） | `addTable` |
| 判断の分かれ道 | **判断フロー**（条件をラベルにした分岐） | `box`+`arrow` |

## 3. 図の作法（構造・フローを分かりやすくする）

- **流れは一方向**：左→右、または上→下。逆流・交差する矢印を作らない。
- **1図1メッセージ、要素は5〜9個**。超えるなら分割するか上位概念でまとめる。
- **「誰が」を必ず明示**する（担当の箱・レーン）。主体のない手順は実行されない手順。
- **ステップは動詞で始め**（「申請する」「審査する」）、番号を振る。
- **色に意味を固定**：主色＝通常の主役、強調色＝関門・Ask・推奨のみ（1スライドに1〜2か所）、グレー＝補助。凡例なしで読めること。
- **矢印の意味は1種類**（時間・因果・お金のどれか）。複数あるなら線種と色を変えラベルを付ける。
- 図の中の文字は**12pt以上**。入りきらなければ文言を削る（縮めない）。
- 図は**ネイティブ図形で作る**（画像化しない）。幹部が自分で直せる。
- 数字は**大きく**（KPIは36pt以上の数字＋小さな単位・説明）。
- 出典と時点を各スライド下部に10.5ptで置く。

## 4. タイポグラフィとレイアウト（本文10.5pt以上、見出しは階層ごとに大きく）

| 要素 | サイズ | 備考 |
|---|---|---|
| スライドタイトル | 30pt 太字 | 結論の文。全頁で位置・サイズ・揃えを統一 |
| リード（タイトル下の1行） | 17pt 標準 | 要点の補足。色は一段淡く |
| 章名・出典・頁 | 10.5pt | フッタ。絶対下限。章名は「施策体系　5」の形で右（§4.5） |
| 見出し（箱の題） | 21pt 太字 | |
| 本文・図中ラベル | 14〜17pt | 図の中の文字も12pt未満にしない（表の本文のみ12pt可）。収まらなければ文言を削る |
| 大型数字・主役の活字 | 62〜185pt 標準ウェイト | §4.6の尺度から選ぶ。太字にしない |

- キャンバスは `LAYOUT_WIDE`（13.33×7.5インチ）。左右余白0.75、本文領域は縦1.9〜6.9。タイトル・リード・本文・出典の左端は全頁で同じx（§4.6）。
- 日本語フォントは **Meiryo**。文字が収まる箱は**1割の余裕**を持つ（QA描画はフォント代替で幅がずれる）。
- 本文は左揃え。中央揃えはタイトルと数字だけ。
- **配色は内容から導く**。実務・決裁の既定は、白＋ネイビー（`1F3A5F`）＋強調の朱（`C2410C`）。環境なら深緑、福祉なら温かいテラコッタなど、領域の意味に合わせて `P` を差し替える。強い主色1＋抑えた背景＋鋭い強調1。
- 章扉は画像ではなく**タイポグラフィ**（大きな章番号＋章題）。

## 4.5 視覚設計：読みたくなる第一印象と、記憶に残る山場（型B・Cの方針説明）

構造がわかりやすいだけでは、読み手は読みたくならない。市長・副市長への方針説明では、次の5つを先に決めてから作る。KF R9実施方針（令和8年11月）で、3案の試作と3人のレビューにより検証した。

1. **世界観は、色と活字だけで作る。** 題材から色の気分を導く（例：川崎の臨海の夜＝深い紺）。色は4役だけ：夜 `0B1730`、紙 `F4F6FA`、ネイビー `1F3A5F`、朱（淡色面 `B93A14`／濃色面 `F28A62`）。面積は紙・夜・ネイビー系が9割、朱は1割未満。全面の濃色ページは、表紙＋山場2枚（効果・財政、最終のAsk）の3枚まで。表紙・付録の扉も、夜色の単色面と大きな活字で作る。
2. **1ページに主役は1つ。他の3倍以上の大きさにする。** 主役は活字（巨大な数字や短い言葉）：「R9」185pt、「法人格がない」89pt、「共催／主催」89pt、「ご了承を、」107pt（§4.6の尺度の値。本文14ptの約13倍まで）。主役は細い書体（日本語は游明朝、数字・欧文はCambria）の標準ウェイトで組み、太字にしない。図は路線図（番号付きの駅）、原因から答えへの1本の矢印、2つの対比で語る。
3. **強調色の意味を固定する。** 朱＝期限・関門・Ask・推奨だけ、1ページ1〜2か所。濃色面は `F28A62`（札の字は夜色）、淡色面は `B93A14`（札の字は白）。彩度を抑えた朱にする（高彩度の朱は上品さを欠く）。同じ語（例「12月中旬まで」）は、全ページで同じ言い方・同じ色・30pt・同じ札の大きさ（幅約3.1インチ×高さ0.74）にする（期限札。作り方は§4.6）。
4. **画像は作らない。** 生成画像（numpy・PILによる夜景など）は質が上がらず、表紙や扉に置いても安っぽく見える。文字の読みやすさ・印刷・手直しのしやすさも落とす。使うのは、質の高い素材（実写など）を木村さんが渡したときだけ。印刷・回覧する版は白基調に切り替える。
5. **線種で確かさを語る。** 実線＝確定、破線＝未確定・目標。数値は、図形の大小・高さで値を暗示しない（階段や棒の高さで見せない）。目標値には必ず「（目標）」を同じ行に付ける。

**使ってよい面：** 結論を載せる夜色の帯（左端から伸びる、高さ1インチ前後）は可。細い縦の色帯・タイトル下の線は不可。

**使わない（レビューで指摘された失敗）：** 円の中のアイコン／縦書き（LibreOfficeで後続の文字に重なる）／黄・琥珀／警告色の平塗りブロック／値を暗示する図形（上り階段・傾く点線）／画像（表紙・扉を含む）／文字の背後の飾りの帯／「0円」の単位だけ大きく、範囲ラベルを小さくすること（範囲ラベルは同じ行に24pt以上）／太字の連発（太字は題とラベルだけ）／尺度外の文字サイズ／本文14ptの15倍を超える巨大文字／高彩度の朱や太い枠線（上品さを欠く）／頁番号の振り直し・項目順の入れ替え（既存資料の改版時）。

**検証の進め方（重要案件）：**
- 方向を3つ決めて、別々のエージェントに試作させる：A エディトリアル（活字が主役）／B 図解（路線図）／C 配色と余白の世界観（夜色×紙色）。各エージェントは3〜5回、自己点検して磨く。
- 別のレビュー3役（読み手・視覚・事実）が、6軸で採点する：①1秒の印象 ②独自性 ③階層・活字 ④図の力 ⑤統一とリズム ⑥実装性・印刷。あわせて、頁ごとの勝者と融合案を出させる。
- 融合版を1つ作り、全ページを描画して目視する。
- Codexなど別のエージェントを使うときは、同じ指示書（エージェントに依存しない書き方）を渡し、方向D（自由）として加える。作品は同じ6軸で比べる。

**部品（pptxgenjs。KF R9 v5で実証。`T`・`ln`・`rect` は §7 と同様の薄いラッパ）：**

```js
// 期限札：全頁で同じ語・同じ色。dark=濃色面なら明るい朱＋夜色の字
function plate(s, x, y, w, h, text, fs, dark) {
  s.addText(text, { shape: pres.ShapeType.rect, x, y, w, h, fontFace: "Meiryo", fontSize: fs, bold: true,
    color: dark ? "0B1730" : "FFFFFF", fill: { color: dark ? "F28A62" : "B93A14" }, line: { color: dark ? "F28A62" : "B93A14", width: 0 },
    align: "center", valign: "middle", margin: 0, isTextBox: true });
}
// 確定／未確定の札：実線＝確定（塗り）、破線＝未確定
function tag(s, x, y, w, text, solid) {
  s.addText(text, { shape: pres.ShapeType.rect, x, y, w, h: 0.3, fontFace: "Meiryo", fontSize: 12, bold: true,
    color: solid ? "FFFFFF" : "1F3A5F", fill: { color: solid ? "1F3A5F" : "F4F6FA" },
    line: { color: "1F3A5F", width: 1.25, dashType: solid ? undefined : "dash" }, align: "center", valign: "middle", margin: 0, isTextBox: true });
}
// 数字と単位を別の箱で置く（和欧のすき間を避け、下端をそろえる）。parts=[{t,fs,num}]
function numline(s, x, yb, parts, color) {
  const wd = p => (p.num ? 0.56 * p.t.length : p.t.length) * p.fs / 72; let cx = x;
  parts.forEach(p => { const w = wd(p) + 0.12, h = p.fs / 72 * 1.25, raise = p.num ? 0 : (0.21 * parts[0].fs - 0.12 * p.fs) / 72;
    s.addText(p.t, { x: cx - 0.02, y: yb - h - raise, w, h, fontFace: p.num ? "Arial" : "Meiryo", fontSize: p.fs, bold: true, color, margin: 0, valign: "bottom", align: "left", wrap: false, isTextBox: true });
    cx += wd(p); });
}
```

路線図（誰が・いつ・何をする流れ）は、主体ごとの横線（レーン）の上に、番号付きの駅を左から右へ並べ、駅の間を太い線でつなぐ。関門の駅だけ朱で塗る（白い番号）。ラベルは駅の上か下に置き、線に触れさせない。段階の見出し帯は横に並べ、最後の段階（支払など）だけ夜色にする。

折り返しは、LibreOfficeとMeiryoで幅が違うため、日本語の長めの文は `\n` で句の切れ目に改行を入れ、1行は全角13字前後（17pt、幅3.8インチの列）以内にする。1字だけの折り返しを残さない。

## 4.6 上品さの設計（デザイン科学）：インパクトと上品さを両立する

木村さんの基準は「**視覚的インパクトは出す。ただし、上品さを欠くことは許されない**」。印象が強いだけの資料は、色・文字の大きさ・太さ・余白の釣り合いが崩れている。KF R9のv5（インパクト重視）をv6で整え直し、数値で確かめた（文字サイズ33種→13種、太字55%→39%、コントラスト不足あり→なし）。作る前に次の8つを決め、作った後に監査スクリプトで確かめる。

1. **活字は尺度から選ぶ（比およそ1.2）。** 使ってよいサイズは 10.5／12／14／17／21／25／30／36／43／62／89／107／185pt だけ。1資料で使う種類は13以内。役割：10.5＝出典・頁、12＝図の注・表の本文、14＝本文・図中ラベル、17＝リード・強調本文、21＝見出し、25＝帯の結論、30＝タイトル・期限札、36〜43＝見出しの大字、62〜185＝主役。尺度外の値（例：27pt、13pt、300pt）は、釣り合いを崩す原因になる。
2. **太字は、題とラベルだけ。** 太字の文字数は全体の4割以下。本文・表の中身・帯の補足は標準ウェイト。大きな文字ほど細く見せる。太い巨大文字は品を落とす。
3. **書体は2系統。** 本文・ラベルは Meiryo。主役の大字は、日本語が游明朝（Yu Mincho）標準、数字・欧文が Cambria 標準。主役は本文14ptの13倍まで（300ptや220ptは過大）。
4. **余白と格子。** 左右余白0.75インチ。タイトル・リード・本文・出典の左端を全頁で同じxにそろえる。3列の段組みは列間0.4インチ。頁ごとの左端の種類は少なく（図の頁は除く）。
5. **色の釣り合い。** 紙 `F4F6FA`／夜 `0B1730`／ネイビー `1F3A5F`／中 `3F6C9E`／淡 `8FB0D3`／朱 `B93A14`（濃色面は `F28A62`）。朱は1頁2か所まで。コントラスト比は、文字4.5以上、24pt以上の大字は3以上。淡 `8FB0D3` は紙の上の文字に使わない。白い文字は `3F6C9E` 以上に濃い面の上に置く（`4F7CAC` は4.36で不足）。濃色面の文字は、白と淡青 `B7C4D9` の2色だけ。
6. **線は細く。** 罫0.75pt、強調の罫1.5pt、矢印2pt、路線2.5pt。濃色面の罫は夜より少し明るい紺 `2C3E5E`（色の濃淡だけで引く）。
7. **面の使い方。** 全面の濃色は表紙・山場・Ask・付録扉の4枚まで。結論の帯は端から端まで。色面の上にさらに色面を重ねない。
8. **期限札は印判のように。** 朱の塗りに、内側0.05インチの細い枠線を1本（字色、透明度55%）。全頁で同じ語・30pt・幅約3.1インチ。幅が足りないと「12月中旬ま／で」と折り返すので、3.0インチ未満にしない。

```js
// 期限札（v6）：塗り＋内側の細い枠。dark=濃色面
function plate(s, x, y, w, h, text, dark) {
  const fill = dark ? "F28A62" : "B93A14", tx = dark ? "0B1730" : "FFFFFF";
  s.addText(text, { shape: pres.ShapeType.rect, x, y, w, h, fontFace: "Meiryo", fontSize: 30, bold: true, color: tx,
    fill: { color: fill }, line: { color: fill, width: 0 }, align: "center", valign: "middle", margin: 0, isTextBox: true, charSpacing: 1 });
  s.addShape(pres.ShapeType.rect, { x: x + 0.05, y: y + 0.05, w: w - 0.1, h: h - 0.1,
    fill: { color: fill, transparency: 100 }, line: { color: tx, width: 0.75, transparency: 55 } });
}
```

**監査（作った後に必ず実行）。** 次を `audit.py` として保存し、`python3 audit.py deck.pptx --dark 1,8,11,12`（濃色頁の番号）で実行する。目標は「尺度外のサイズ: なし／10.5pt未満: なし／コントラスト不足: なし／太字の比率40%以下／使用サイズ13種以内」。外れたら直してから見せる。

```python
import sys, collections
from pptx import Presentation
SCALE = [10.5,12,14,17,21,25,30,36,43,62,89,107,128,154,185,222]
def lum(h):
    c = [int(h[i:i+2],16)/255 for i in (0,2,4)]
    c = [x/12.92 if x <= 0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]
def cr(a, b):
    la, lb = lum(a), lum(b); return (max(la,lb)+0.05)/(min(la,lb)+0.05)
def fill_hex(sh):
    try:
        if sh.fill.type == 1: return str(sh.fill.fore_color.rgb)
    except Exception: pass
def main(path, dark):
    prs = Presentation(path); IN = 914400
    sizes = collections.Counter(); bold = runs = 0; off = collections.Counter(); low = []; bad = []; edges_n = {}
    for n, s in enumerate(prs.slides, 1):
        bg = '0B1730' if n in dark else 'F4F6FA'; shapes = list(s.shapes); edges = set()
        for i, sh in enumerate(shapes):
            if not sh.has_text_frame or not sh.text_frame.text.strip(): continue
            cx = (sh.left+sh.width/2)/IN; cy = (sh.top+sh.height/2)/IN
            under = fill_hex(sh)
            if not under:
                for k in range(i-1, -1, -1):          # 直近（最上）の塗りを背景とみなす
                    o = shapes[k]; h = fill_hex(o)
                    if h and o.left/IN <= cx <= (o.left+o.width)/IN and o.top/IN <= cy <= (o.top+o.height)/IN:
                        under = h; break
                under = under or bg
            edges.add(round(sh.left/IN/0.05)*0.05)
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if not r.text.strip() or not r.font.size: continue
                    sz = r.font.size.pt; sizes[sz] += len(r.text); runs += 1; bold += 1 if r.font.bold else 0
                    if sz < 10.5: low.append((n, sz, r.text[:12]))
                    if sz not in SCALE: off[sz] += 1
                    try:
                        col = str(r.font.color.rgb); ratio = cr(col, under)
                        if ratio < (3.0 if sz >= 24 else 4.5): bad.append((n, round(ratio,2), col, under, r.text[:10]))
                    except Exception: pass
        edges_n[n] = len(edges)
    print('サイズ(pt:文字数)', sorted(sizes.items())); print('尺度外のサイズ:', dict(off) or 'なし', ' 種類:', len(sizes))
    print('太字の比率: %.0f%%' % (100*bold/max(runs,1))); print('10.5pt未満:', low or 'なし'); print('コントラスト不足:', bad or 'なし')
    print('最大/本文(14)比: %.1f' % (max(sizes)/14)); print('左端の種類数:', edges_n)
if __name__ == '__main__':
    d = {int(x) for x in sys.argv[sys.argv.index('--dark')+1].split(',')} if '--dark' in sys.argv else set()
    main(sys.argv[1], d)
```

**描画と実機の差。** QA描画（LibreOffice）には Cambria と Meiryo がなく、代わりの書体で幅がずれる。主役の欧文・数字は幅に15%の余裕を持たせ、日本語の長文は `\n` で句の切れ目に改行する。「0 円」のような和欧のすき間はLibreOfficeだけの現象で、PowerPointには出ない（数字と単位は別の箱で下端をそろえる）。最終の見た目の確認は、PowerPointの実機で行うよう依頼者に伝える。

## 5. デザイン3案の出し方

内容に応じて3つの方向性を示し、推奨を選ぶ。

| 案 | 向く場面 | 特徴 |
|---|---|---|
| 端正な行政文書型 | 局長・市長への決裁・協議（型B・C） | 白基調、罫と表と図が主役、強調色は関門のみ |
| エディトリアル型 | 市長への方針説明、外部講演の本編 | 大きな結論の文、広い余白、数字を巨大に、図は少数精鋭 |
| 投影重視の暗色型 | 暗い会場での外部発表（型A） | 暗背景、白の大文字、強調色1。**印刷しない場合のみ** |
| 夜色×活字型（KF R9で採用） | 市長・副市長への山場の方針説明（型B。投影＋白版を印刷） | 画像なし。活字尺度・細い書体の主役・抑えた朱で上品に（§4.6）。本編の大半は紙色、濃色は表紙＋山場2枚。主役は巨大な活字、図は路線図、朱は期限札・関門・推奨だけ（§4.5） |

## 6. 相手別の注意

- **市長・局長**：結論とAskを1枚目で。想定問答を別紙で用意。
- **社長・経営層（民間）**：投資対効果（金額・回収期間・リスク）を数字で。政策用語は事業用語に言い換える。
- **印刷・回覧**：白基調。A4/A3縮小でも読めるか確認（本文12pt以上）。

## 7. 実装：検証済みレイアウト部品（pptxgenjs）

以下を `lib.js` として保存し `require` して使う。施策体系図・スイムレーン・ステップ・ロードマップ・比較表がずれずに組める（実機で全スライドを描画確認済み）。色は `P` を差し替える。

```js
// ===== exec-slides lib (pptxgenjs) =====
const pptxgen = require("pptxgenjs");
const W = 13.333, MX = 0.6, CT = 1.85, CB = 6.85, CW = W - 2 * MX;
const F = "Meiryo";
const P = { ink:"1B1D21", sub:"5F6672", line:"D5DAE1", panel:"F3F5F8", main:"1F3A5F", main2:"E4EAF3", accent:"C2410C", accent2:"FCEBDD", ok:"2F7D5B" };

function newDeck(title) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; pres.title = title;
  pres.defineSlideMaster({ title: "BODY", background: { color: "FFFFFF" },
    objects: [{ placeholder: { options: { name: "title", type: "title", x: MX, y: 0.72, w: CW, h: 0.95,
      fontFace: F, fontSize: 26, bold: true, color: P.ink, align: "left", valign: "top", margin: 0 }, text: "" } }],
    slideNumber: { x: W - MX - 0.6, y: 7.05, w: 0.6, h: 0.3, fontFace: F, fontSize: 10.5, color: P.sub, align: "right" } });
  return pres;
}
function T(s, text, o) { s.addText(text, Object.assign({ fontFace: F, isTextBox: true, margin: 0, valign: "top", color: P.ink, fontSize: 14 }, o)); }
function frame(pres, tag, title, source) {            // 標準フレーム：章タグ＋結論タイトル＋出典
  const s = pres.addSlide({ masterName: "BODY" });
  T(s, tag, { x: MX, y: 0.38, w: 8, h: 0.3, fontSize: 12, bold: true, color: P.main });
  s.addText(title, { placeholder: "title" });
  if (source) T(s, source, { x: MX, y: 7.05, w: CW - 1, h: 0.3, fontSize: 10.5, color: P.sub });
  return s;
}
function box(pres, s, x, y, w, h, text, o = {}) {      // 角丸ボックス（図の基本部品）
  s.addText(text, Object.assign({ shape: o.round === false ? pres.ShapeType.rect : pres.ShapeType.roundRect, rectRadius: 0.06,
    x, y, w, h, fontFace: F, fontSize: 14, color: P.ink, align: "center", valign: "middle", margin: 0.08,
    fill: { color: P.panel }, line: { color: P.line, width: 0.75 } }, o));
}
function arrow(pres, s, x1, y1, x2, y2, o = {}) {      // 直線矢印（向きは自動）
  s.addShape(pres.ShapeType.line, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    flipH: x2 < x1, flipV: y2 < y1,
    line: { color: o.color || P.sub, width: o.width || 1.5, endArrowType: o.head === false ? undefined : "triangle" } });
}
function elbow(pres, s, x1, y1, x2, y2, o = {}) {      // 親→子のL字連結（x方向に折れる）
  const mx = (x1 + x2) / 2;
  arrow(pres, s, x1, y1, mx, y1, { ...o, head: false });
  arrow(pres, s, mx, y1, mx, y2, { ...o, head: false });
  arrow(pres, s, mx, y2, x2, y2, o);
}
function badge(pres, s, x, y, n, d = 0.42, fill = P.main) {  // 番号バッジ
  s.addText(String(n), { shape: pres.ShapeType.ellipse, x, y, w: d, h: d, fontFace: F, fontSize: 14, bold: true,
    color: "FFFFFF", fill: { color: fill }, align: "center", valign: "middle", margin: 0 });
}
// 施策体系図：目的 → 施策の柱 → 事業 → 指標（左から右へ。柱ごとに事業が束になる）
function tree(pres, s, d) {
  const cols = [ [MX, 2.3], [3.3, 2.7], [6.5, 3.6], [10.6, 2.13] ];
  const heads = ["目的", "施策の柱", "事業（具体的方策）", "成果指標"];
  heads.forEach((h, i) => T(s, h, { x: cols[i][0], y: CT, w: cols[i][1], h: 0.3, fontSize: 12, bold: true, color: P.sub, align: "center" }));
  const top = CT + 0.45, avail = CB - top;
  const n = d.pillars.length, gap = 0.2, ph = (avail - gap * (n - 1)) / n;
  box(pres, s, cols[0][0], top, cols[0][1], avail, d.purpose, { fill: { color: P.main }, color: "FFFFFF", bold: true, fontSize: 18, line: { color: P.main } });
  d.pillars.forEach((p, i) => {
    const y = top + i * (ph + gap);
    box(pres, s, cols[1][0], y, cols[1][1], ph, [{ text: p.no + "  ", options: { bold: true, color: P.main } }, { text: p.name, options: { bold: true } }],
        { fill: { color: P.main2 }, line: { color: P.main2 }, fontSize: 15 });
    elbow(pres, s, cols[0][0] + cols[0][1], top + avail / 2, cols[1][0], y + ph / 2);
    T(s, p.projects.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < p.projects.length - 1 } })),
      { x: cols[2][0] + 0.1, y, w: cols[2][1] - 0.1, h: ph, fontSize: 13, valign: "middle", paraSpaceAfter: 3 });
    arrow(pres, s, cols[1][0] + cols[1][1], y + ph / 2, cols[2][0], y + ph / 2);
    box(pres, s, cols[3][0], y, cols[3][1], ph, p.kpi, { fill: { color: "FFFFFF" }, line: { color: P.main, width: 1 }, fontSize: 13 });
    arrow(pres, s, cols[2][0] + cols[2][1], y + ph / 2, cols[3][0], y + ph / 2);
  });
}
// 施策フロー（スイムレーン）：主体×フェーズ。tasks=[{lane,phase,text,key?}], links=[[i,j]]
function swimlane(pres, s, d) {
  const lx = MX, lw = 1.7, gx = lx + lw, gw = CW - lw, top = CT, hh = 0.45;
  const pw = gw / d.phases.length, lh = (CB - top - hh) / d.lanes.length;
  d.phases.forEach((p, i) => box(pres, s, gx + i * pw + 0.03, top, pw - 0.06, hh, p, { fill: { color: P.main }, color: "FFFFFF", bold: true, fontSize: 13, line: { color: P.main } }));
  d.lanes.forEach((l, i) => {
    const y = top + hh + i * lh;
    s.addShape(pres.ShapeType.rect, { x: lx, y: y + 0.03, w: CW, h: lh - 0.06, fill: { color: i % 2 ? "FFFFFF" : P.panel }, line: { color: P.line, width: 0.5 } });
    T(s, l, { x: lx + 0.1, y, w: lw - 0.2, h: lh, fontSize: 13, bold: true, color: P.main, valign: "middle" });
  });
  const pos = d.tasks.map(t => {
    const bw = pw - 0.3, bh = Math.min(lh - 0.3, 0.9);
    const x = gx + t.phase * pw + 0.15, y = top + hh + t.lane * lh + (lh - bh) / 2;
    box(pres, s, x, y, bw, bh, t.text, Object.assign({ fontSize: 13, fill: { color: "FFFFFF" }, line: { color: P.main, width: 1 } }, t.key ? { fill: { color: P.accent2 }, line: { color: P.accent, width: 1.25 } } : {}));
    return { x, y, bw, bh };
  });
  (d.links || []).forEach(([a, b]) => {
    const A = pos[a], B = pos[b];
    if (A.x === B.x) {                                   // 同じ列：縦矢印（上下の辺どうしを結ぶ）
      const down = B.y > A.y;
      arrow(pres, s, A.x + A.bw / 2, down ? A.y + A.bh : A.y, B.x + B.bw / 2, down ? B.y : B.y + B.bh);
    } else if (A.y === B.y) arrow(pres, s, A.x + A.bw, A.y + A.bh / 2, B.x, B.y + B.bh / 2);
    else elbow(pres, s, A.x + A.bw, A.y + A.bh / 2, B.x, B.y + B.bh / 2);
  });
}
// ステップ・フロー（1行）：[{h, b, who}]
function flow(pres, s, steps, y = CT + 0.8, h = 3.0) {
  const n = steps.length, g = 0.35, w = (CW - g * (n - 1)) / n;
  steps.forEach((st, i) => {
    const x = MX + i * (w + g);
    box(pres, s, x, y, w, h, "", { fill: { color: P.panel } });
    badge(pres, s, x + 0.15, y + 0.15, i + 1);
    T(s, st.h, { x: x + 0.15, y: y + 0.7, w: w - 0.3, h: 0.6, fontSize: 16, bold: true });
    T(s, st.b, { x: x + 0.15, y: y + 1.35, w: w - 0.3, h: h - 1.5, fontSize: 14, color: P.ink });
    if (st.who) box(pres, s, x, y + h + 0.15, w, 0.42, st.who, { fill: { color: P.main2 }, line: { color: P.main2 }, fontSize: 12, bold: true, color: P.main });
    if (i < n - 1) arrow(pres, s, x + w + 0.03, y + h / 2, x + w + g - 0.03, y + h / 2, { color: P.main, width: 2 });
  });
}
// ロードマップ（ガント）：periods=["R8下",...], rows=[{name,from,to,gate?,label?}] from/toは期間index
function roadmap(pres, s, d) {
  const nw = 2.9, gx = MX + nw, gw = CW - nw, top = CT, hh = 0.45, n = d.periods.length, pw = gw / n;
  const rh = Math.min(0.62, (CB - top - hh) / d.rows.length);
  d.periods.forEach((p, i) => box(pres, s, gx + i * pw + 0.02, top, pw - 0.04, hh, p, { fill: { color: P.main }, color: "FFFFFF", bold: true, fontSize: 12, line: { color: P.main } }));
  d.rows.forEach((r, i) => {
    const y = top + hh + 0.08 + i * rh;
    if (i % 2 === 0) s.addShape(pres.ShapeType.rect, { x: MX, y, w: CW, h: rh, fill: { color: P.panel }, line: { color: P.panel, width: 0 } });
    T(s, r.name, { x: MX + 0.1, y, w: nw - 0.2, h: rh, fontSize: 13, valign: "middle", bold: !!r.head });
    s.addShape(pres.ShapeType.roundRect, { x: gx + r.from * pw + 0.05, y: y + rh * 0.2, w: (r.to - r.from + 1) * pw - 0.1, h: rh * 0.6, rectRadius: 0.05,
      fill: { color: r.gate ? P.accent : P.main }, line: { color: r.gate ? P.accent : P.main, width: 0 } });
    if (r.label) T(s, r.label, { x: gx + r.from * pw + 0.15, y: y + rh * 0.2, w: (r.to - r.from + 1) * pw - 0.3, h: rh * 0.6, fontSize: 11, color: "FFFFFF", valign: "middle", bold: true });
  });
}
// 選択肢比較表：criteria=[...], options=[{name, vals:[...], rec?}]
function options(pres, s, d) {
  const hdr = [{ text: "評価軸", options: { fill: { color: P.main }, color: "FFFFFF", bold: true } }].concat(
    d.options.map(o => ({ text: o.name + (o.rec ? "（推奨）" : ""), options: { fill: { color: o.rec ? P.accent : P.main }, color: "FFFFFF", bold: true, align: "center" } })));
  const rows = d.criteria.map((c, i) => [{ text: c, options: { bold: true, fill: { color: P.panel } } }].concat(
    d.options.map(o => ({ text: o.vals[i], options: { align: "center", fill: { color: o.rec ? P.accent2 : "FFFFFF" } } }))));
  const cw0 = 2.3, cw = (CW - cw0) / d.options.length;
  s.addTable([hdr, ...rows], { x: MX, y: CT, w: CW, colW: [cw0].concat(d.options.map(() => cw)), fontFace: F, fontSize: 13, color: P.ink,
    border: { type: "solid", color: P.line, pt: 0.75 }, valign: "middle", rowH: Math.min(0.95, (CB - CT) / (d.criteria.length + 1)), margin: [0.05, 0.1, 0.05, 0.1] });
}
module.exports = { pptxgen, W, MX, CT, CB, CW, F, P, newDeck, T, frame, box, arrow, elbow, badge, tree, swimlane, flow, roadmap, options };
```

**使い方**

```js
const L = require("./lib.js"); const { P, MX, CT, CB, T, box } = L;
const pres = L.newDeck("件名");
let s = L.frame(pres, "02 施策体系", "施策は3本の柱で構成し、柱ごとに事業と成果指標を結ぶ", "出典：○○（令和8年）");
L.tree(pres, s, { purpose: "目的の文", pillars: [{ no: "1", name: "柱の名", projects: ["事業A", "事業B"], kpi: "指標\n現状→目標" } /* 2〜4本 */] });
s = L.frame(pres, "03 施策フロー", "…", "出典：…");
L.swimlane(pres, s, { phases: ["相談", "申請"], lanes: ["民間事業者", "市"], tasks: [{ lane: 0, phase: 0, text: "企画を相談" }, { lane: 1, phase: 1, text: "審査する", key: true }], links: [[0, 1]] });
s.addNotes("台本…");
pres.writeFile({ fileName: "out.pptx" });
```

- 柱は2〜4本、スイムレーンの主体は2〜4、フェーズは3〜6が読みやすい。超えるなら分割する。
- 表紙・サマリー・Askは `box` と `T` で組む（サマリーは左に濃色のAskパネル、右に番号付きの要点3つが定石）。
- 部品にない図（事業スキーム図など）は `box` と `arrow` を組み合わせる。矢印にラベルを書く場合は `T` を矢印の中点に置く。
- チャートはネイティブ（`addChart`）。`valAxisMinVal: 0`、軸・凡例・データラベルを全チャートで統一する。

## 8. 政策説明スライドの自己点検

- [ ] 型を言語化でき、型B・C・D・Gに装飾画像がない。印刷・回覧される資料が白基調
- [ ] Askが2枚目のサマリーと最終枚にある（決めてほしいこと・期限）
- [ ] タイトルだけを通読して話が通る（結論の文になっている）
- [ ] 1スライド1メッセージ。図の要素は9個以内。文字だけのスライドがない
- [ ] 体系図とフローに「誰が・いつ・何を」がある。矢印が一方向で、ボックスを貫通していない
- [ ] 選択肢に「やらない／延期」があり、推奨の理由は3つ以内
- [ ] 数値に出典と時点があり、推計・目標値は明示。留保が添えてある
- [ ] 文字サイズは§4.6の尺度13種以内。本文14pt以上（表の本文のみ12pt可）・注記10.5pt以上。見出しは階層ごとに大きい。太字は4割以下
- [ ] 強調色は関門・Ask・推奨のみ。影・絵文字・下線・細い色帯がない
- [ ] 全ページに主役が1つあり、他の3倍以上の大きさ。縮小（幅320px）で見ても主役が見える
- [ ] 全面濃色は3枚以内。期限の語（例「12月中旬まで」）が全ページで同じ言い方・同じ色・28pt以上
- [ ] 目標値に「（目標）」が同じ行にある。図形の大小・高さが値を暗示していない。実線＝確定、破線＝未確定
- [ ] 画像・アイコン・縦書き・黄・警告色の平塗り・飾りの帯がない（表紙・扉も色面と活字だけ）。1字だけの折り返しがない
- [ ] 上品さ：主役は細い書体の標準ウェイトで本文の13倍以内。朱は1頁2か所まで・彩度を抑えた値。余白0.75・左端がそろう。`audit.py` の出力（尺度外・コントラスト不足・太字比率）が基準内
- [ ] 全ページを描画して目視した（はみ出し・重なり・矢印の貫通・1文字だけの折り返し）
- [ ] `validate.py` が通り、`deliverable-verifier` で数値・出典・論理を検証した
- [ ] デザインの理由を1行で言える（言えないなら、まだ考えていない）

---

# 【型A・F・E】高密度ビジュアル基準（講演・広報・技術解説・顧客説明）

以下の§0〜§8は型A・F・E（講演・広報・技術解説・顧客説明）の基準。**型B・C・D・Gには、§1（必須要件）・§2〜§3（画像生成）・§5の構成の型（全面ヒーロー等）を適用しない。** §5の「技術的な地雷」、§6（品質保証）、§7（中身の質）は全型共通で適用する。

文字と棒グラフだけの資料は不合格。型A・F・Eでは以下を必須要件として満たすこと。

---

## 0. 最初にやること

1. 実データを一次情報から集める（**リサーチが先、書式スキルは後**）
2. `AskUserQuestion` で用途・聴衆・枚数・トーンを確認（既に会話で確定済みなら省略）
3. **ビジュアル計画を先に立てる**：どのセクションに何の絵を置くかを列挙してから着手する

---

## 1. 絶対的な必須要件（これを下回ったら未完成）

| 項目 | 最低ライン |
|---|---|
| 生成画像 | **20点以上**（ヒーロー／章扉／概念図／アイコン） |
| チャート種類 | **6種類以上**（棒・線・ドーナツ・散布/バブル・ガント・面 など） |
| 説明用の概念図 | **5点以上**（装飾ではなく「仕組みを説明する」図） |
| 視覚要素ゼロの面 | **0**（全スライド・全セクションに必ず絵か図がある） |
| 章扉 | 主要セクションごとに**フルブリード画像**の扉を置く |
| アイコン | 統一されたセットを生成して使う（絵文字は禁止・環境依存で豆腐化する） |

---

## 2. 画像は「生成する」

Adobeの各ツールは**画像編集専用で生成はできない**。Adobe Stockもニッチ題材ではヒットしない。
→ **Python（numpy + PIL）で物理・数理に基づく画像を自前レンダリングする**のが唯一確実な経路。著作権もクリーン。

### レンダリングの型（この構造をそのまま使う）

```python
# 1) float32 の加算バッファで「光」を積む
# 2) 背景 = 複数の放射状グラデーション（nebula）＋微粒子
# 3) 発光レイヤ = PIL ImageDraw で細い線と点を描く
# 4) bloom = 複数半径のガウスぼかしをスクリーン合成（必ずミップで縮小してから！）
# 5) 仕上げ = ビネット＋フィルムグレイン
```

**bloomは必ず縮小して処理する**。フル解像度で半径120のガウスをかけると数分かかりタイムアウトする。

```python
def bloom(core_img, passes=((6,.55),(18,.42),(52,.30),(120,.20))):
    W,H = core_img.size; acc = np.zeros((H,W,3), np.float32)
    for radius, strength in passes:
        k = max(1, int(radius/5))
        small = core_img.resize((max(8,W//k), max(8,H//k)), Image.BILINEAR)
        small = small.filter(ImageFilter.GaussianBlur(max(1.0, radius/k)))
        acc = screen(acc, f(small.resize((W,H), Image.BILINEAR)) * strength)
    return acc
```

### 実行時の注意（過去に踏んだ地雷）

- **バックグラウンド実行（`nohup ... &`）は途中で殺される。** 必ず引数で対象を指定し、**3〜4点ずつ前景で分割実行**する
- 生成後は**必ず全ファイルの整合性を検証**（`Image.open(p).load()`）。中断で truncated PNG が残る
- 生成が終わったらコンタクトシートを作って**必ず自分の目で見る**

---

## 3. 暗幕（スクリム）は画像に焼き込む

画像の上に文字を置くときの暗幕を、**矩形の重ね置きで作ってはいけない**。段差が縞になって必ず見える。
→ **Pythonでグラデーションを画像に乗算して焼き込む**。

```python
def rampH(w,a,b,p=1.0):
    t = np.linspace(0,1,w,dtype=np.float32)**p
    return a+(b-a)*t
arr = arr * rampH(w, 0.13, 1.0, 0.75)[None,:,None]   # 左を暗く
```

---

## 4. HTML成果物

- **完全自己完結**：画像はWeb最適化（JPEG q82・幅1100〜1920px）して**base64で埋め込む**。外部依存ゼロで単体配布できること
- 埋め込み総量の目安は **2MB以内**（1200px幅・q82なら15点で約1.2MB）
- 構成要素：
  - フルブリードの**ヒーロー画像**
  - 全画面幅の**章扉**（画像＋見出し＋リード、左からのグラデーションで可読性確保）
  - **画像左・論旨右のスプリット**レイアウト
  - `figure` + `figcaption` の図版カード
  - **自前SVGチャート**（IntersectionObserverで初回表示時にアニメーション）
  - 触れるインタラクション（スライダー・ボタン）を最低1つ
- 背景は自前で暗色を敷き、**端末のダーク/ライト設定に依存しない**
- `prefers-reduced-motion` 対応、画面外ではアニメーション停止

---

## 5. PPTX成果物

`pptxgenjs` を使う。**`pres.layout = "LAYOUT_WIDE"` を addSlide より前に設定**（13.3×7.5インチ）。

### 構成の型
- 表紙：**全面ヒーロー画像**
- **章扉スライド**を主要セクションごとに挿入（全面画像＋大きな章番号＋章タイトル）
- 中身：全面／ハーフブリード／上部画像帯／カード内画像 を**混ぜる**。同じ骨格を続けない
- 結論：全面背景画像
- 全スライドに `addNotes()` でスピーカーノート

### 技術的な地雷（すべて実際に踏んだもの）
- 色に `#` を付けない・8桁禁止（ファイルが壊れる）
- **`valAxisMinVal: 0` を全チャートの既定に入れる**。入れないと軸が負値まで伸びる（-1,500量子ビット等）
- 積み上げ棒の `dataLabelPosition` に `outEnd` は禁止（ファイルが壊れる）
- オプションオブジェクトは**呼び出しごとに新規作成**（pptxgenjsが破壊的に書き換える）
- 影の `offset` は0以上／`rectRadius` は `ROUNDED_RECTANGLE` のみ
- **絵文字は使わない**。日本語ラベルか数字か、生成したアイコン画像を使う
- 日本語フォントは **Meiryo**（Windows同梱）。数字はArial

---

## 6. 品質保証（省略不可）

```bash
# PPTX
python <pptxスキル>/scripts/office/validate.py out.pptx
python <pptxスキル>/scripts/office/soffice.py --headless --convert-to pdf out.pptx
pdftoppm -jpeg -r 100 out.pdf s        # 全ページを画像化
# → コンタクトシートにまとめて全ページを必ず目視する
```

チェック観点：**文字のはみ出し／要素の重なり／軸の負値／縞（バンディング）／絵文字の豆腐化／余白の不均一**

HTMLはタグの開閉・`{}`・`()` の対応をパースして検証し、埋め込み画像数とチャート数を数えて要件を満たしているか確認する。

---

## 7. 中身の質（ビジュアルと同格の要件）

- 主張 → 図表 → **留保** の順で構成する。「ただし、こう読むべき」を必ず添える
- 数値には**出典を明記**。推計・逆算・定性評価はその旨を明示する
- 企業ロードマップの到達年は「目標であって実績ではない」と必ず注記
- 川崎市・まちづくり・EBPMへの含意を、可能な場合は必ず1セクション設ける
- 最後に**時間軸別のアクション**（今すぐ／3〜5年／5〜10年）で締める

---

## 8. 完成前の自己点検（型A・F・E）

- [ ] 生成画像20点以上／チャート6種類以上／概念図5点以上
- [ ] 視覚要素のない面がゼロ
- [ ] 章扉がある
- [ ] 縞・はみ出し・重なりがない（全ページ目視済み）
- [ ] HTMLが自己完結（外部依存ゼロ）
- [ ] 出典と留保が明記されている

**1つでも欠けていたら、まだ顧客に出せる水準ではない。**