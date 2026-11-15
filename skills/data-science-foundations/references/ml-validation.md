# 機械学習：検証・評価・説明

## 1. モデルの選び方（表形式のデータ）

| 状況 | まず試す | 理由 |
|---|---|---|
| 基準モデル | 平均・最頻値、線形回帰・ロジスティック回帰 | 比較の出発点。説明しやすい |
| 件数が中〜大、変数の種類が混在 | 勾配ブースティング（LightGBM、XGBoost、CatBoost） | 表形式で安定して強い。欠測やカテゴリを扱いやすい |
| 件数が少ない | 正則化付き線形モデル（Ridge・Lasso）、ランダムフォレスト | 過学習しにくい |
| 画像・文章・音声 | 学習済みモデルの転用（微調整、埋め込み） | 一から学習するより少ないデータで済む |
| 不確実性も知りたい | 分位点回帰、コンフォーマル予測、ベイズモデル | 予測の幅を示せる |

## 2. 過学習を防ぐ分け方

| データの性質 | 分け方 | scikit-learn |
|---|---|---|
| 互いに独立 | 層化k分割 | `StratifiedKFold` |
| 同じ対象が複数行ある（同じ施設の複数月） | 対象ごとにまとめて分ける | `GroupKFold` |
| 時系列 | 過去で学習し、未来で評価 | `TimeSeriesSplit` |
| 空間データ | 地域のまとまりで分ける | `GroupKFold`（区・メッシュのブロックをグループに） |

**リーク（答えの情報の漏れ）の典型**：将来の情報を含む特徴量、目的変数から作った特徴量、分割前に全データで行った標準化・欠測補完・特徴量選択。前処理は `Pipeline` に入れ、分割の内側で行う。

```python
# 誰が：分析担当者が／どのアプリで：JupyterLab か Google Colab で
# 何を：施設ごとの月次データを／どうする：リークを防ぎながらモデルを評価する
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold, cross_validate
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.dummy import DummyRegressor

pre = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)])
model = Pipeline([("pre", pre), ("gbm", HistGradientBoostingRegressor(random_state=0))])
base = Pipeline([("pre", pre), ("dummy", DummyRegressor(strategy="median"))])

cv = GroupKFold(n_splits=5)
for name, est in [("基準", base), ("勾配ブースティング", model)]:
    s = cross_validate(est, X, y, cv=cv, groups=X["facility_id"],
                       scoring=("neg_mean_absolute_error", "r2"))
    print(name, "MAE", -s["test_neg_mean_absolute_error"].mean().round(2),
          "±", s["test_neg_mean_absolute_error"].std().round(2))
```

コードの意味：`Pipeline` は、欠測の穴埋め・カテゴリの変換・モデルを一つにまとめる箱。こうすると、評価用のデータの情報が学習に混ざらない。`GroupKFold` は同じ施設のデータを、学習側と評価側に分けて入れない設定。最後の繰り返しで、単純な基準モデルと比べて、どれだけ誤差が減ったかを見る。

## 3. 評価指標

| 課題 | 指標 | 使いどころ |
|---|---|---|
| 回帰 | MAE（平均絶対誤差） | 単位がそのままで伝わりやすい。外れ値に強い |
| | RMSE | 大きな外れを重く見る |
| | MAPE・WAPE | 割合で伝えたいとき。0に近い値があるとMAPEは不安定 |
| 分類 | 適合率・再現率・F1 | 見逃しと誤警報のどちらが痛いかで選ぶ |
| | PR-AUC | 陽性がまれなとき（空き家、不正、事故）。ROC-AUCより実態に近い |
| | ROC-AUC | 全体の順位付けの力 |
| | 対数損失・ブライアスコア、較正曲線 | 予測確率そのものを使うとき（確率が実態と合っているか） |
| 順位付け・優先度 | 上位k件の的中率、リフト | 点検・訪問の優先順位を付ける業務 |

- 不均衡データで正解率（accuracy）を使わない（99%が陰性なら、全部「陰性」と答えても99%）。
- しきい値は、見逃しの損失と誤警報の費用から決める。0.5に意味はない。

## 4. 説明と解釈

| 手法 | 分かること | 注意 |
|---|---|---|
| 置換重要度 | その変数を崩すと、精度がどれだけ落ちるか | 相関の強い変数同士で分散する |
| SHAP | 個々の予測への、各変数の寄与 | モデルの中の話であり、現実の因果ではない |
| 部分依存・ICE・ALE | 変数を動かしたときの予測の変化 | 相関がある変数ではALEを使う |
| 代理モデル（浅い決定木） | 全体のおおまかな規則 | 元のモデルとの一致度を示す |

「SHAPで〇〇の寄与が大きい」から「〇〇を増やせば結果が良くなる」とは言えない。介入の効果を言うには、`causal-inference.md` の方法が要る。

## 5. 公共分野での点検

- **公平性**：属性（地域、年齢、国籍など）ごとの誤りの率を比べる。代理変数（郵便番号が属性を代弁する）に注意。
- **個人情報**：目的外利用、匿名加工・仮名加工、少数セルの秘匿。条例・法の扱いは `japan-law-research`。
- **運用後の劣化**：入力の分布の変化、精度の定期確認、再学習の基準。
- **人の関与**：モデルは優先順位の参考とし、不利益処分の判断を自動化しない。説明責任の所在を決めておく。
- **再現性**：乱数の種、ライブラリの版、データの時点を記録する。

## 6. 生成AI・LLMを分析に使うとき

- 分類・抽出・要約に使う場合も、**人手で作った正解データで精度を測る**。件数は少なくてよいが、無作為に抜く。
- 出力の揺れ（同じ入力で結果が変わる）を確認し、指示文と版を記録する。
- 数値の計算・集計はLLMにさせず、コードで行う。
- 機密情報・個人情報を外部サービスへ送らない。組織の規程を確認する。
