# PHASE 3：分析・モデリング（STEP 09〜13）の手順とコード

`SKILL.md` の PHASE 3 から読む。手法の選び方・検証・結果の読み方は `data-science-foundations` を併用する。

### ▶ STEP 09：データフレーム可視化

**目的**：分析前に「データを目で見る」。パターン・異常・仮説を発見する。

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 日本語フォント設定
import japanize_matplotlib                    # pip install japanize-matplotlib
# Google Colab の場合:
# !pip install japanize-matplotlib

SAVE_DIR = "output/figures/"
os.makedirs(SAVE_DIR, exist_ok=True)

def visualize_overview(df: pd.DataFrame,
                       value_cols: list,
                       category_col: str = None,
                       time_col: str = None):
    """
    データ概観の4点セット可視化
    ① 分布（ヒストグラム）
    ② 時系列推移
    ③ カテゴリ別箱ひげ図
    ④ 散布図行列（最大4変数）
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("データ概観", fontsize=18, fontweight="bold", y=1.01)

    # ① 分布
    for col in value_cols[:4]:
        axes[0, 0].hist(df[col].dropna(), alpha=0.6, bins=30, label=col)
    axes[0, 0].set_title("① 値の分布（ヒストグラム）")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(True, alpha=0.3)

    # ② 時系列
    if time_col and time_col in df.columns:
        ts = df.groupby(time_col)[value_cols[0]].mean()
        ts.plot(ax=axes[0, 1], marker="o", linewidth=2, color="#2196F3")
        axes[0, 1].set_title(f"② 時系列推移：{value_cols[0]}")
        axes[0, 1].grid(True, alpha=0.3)
    else:
        axes[0, 1].set_visible(False)

    # ③ カテゴリ別箱ひげ図
    if category_col and category_col in df.columns:
        df.boxplot(column=value_cols[0], by=category_col,
                   ax=axes[1, 0], grid=True)
        axes[1, 0].set_title(f"③ {category_col}別分布：{value_cols[0]}")
        plt.sca(axes[1, 0])
        plt.xticks(rotation=45, ha="right")
    else:
        axes[1, 0].set_visible(False)

    # ④ 散布図（変数が2つ以上の場合）
    if len(value_cols) >= 2:
        axes[1, 1].scatter(df[value_cols[0]], df[value_cols[1]],
                           alpha=0.5, color="#4CAF50")
        axes[1, 1].set_xlabel(value_cols[0])
        axes[1, 1].set_ylabel(value_cols[1])
        axes[1, 1].set_title(f"④ 散布図：{value_cols[0]} vs {value_cols[1]}")
        axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    path = f"{SAVE_DIR}01_overview.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"保存：{path}")

visualize_overview(
    df_featured,
    value_cols=["人口増減率", "高齢化率", "人口密度"],
    category_col="行政区",
    time_col="年"
)
```

---

### ▶ STEP 10：EDA（探索的データ分析）

**目的**：統計的手法でデータの構造・関係・異常を深掘りする。

#### EDA 標準セット（4点）：

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def run_eda(df: pd.DataFrame, value_cols: list, save_dir: str = "output/figures/"):
    """
    EDA 標準4点セット
    ① 要約統計量
    ② 相関行列ヒートマップ
    ③ ペアプロット
    ④ 分布の歪み確認（QQプロット）
    """
    import os
    os.makedirs(save_dir, exist_ok=True)

    # ① 要約統計量 ─────────────────────────────
    print("=" * 60)
    print("① 要約統計量")
    print("=" * 60)
    stats = df[value_cols].describe().T
    stats["skewness"] = df[value_cols].skew()        # 歪度（|>1| で非対称）
    stats["kurtosis"] = df[value_cols].kurt()        # 尖度（|>3| で裾が重い）
    stats["missing%"] = df[value_cols].isna().mean() * 100
    print(stats.round(3).to_string())

    # ② 相関行列ヒートマップ ────────────────────────
    print("\n② 相関行列（Pearson）")
    corr = df[value_cols].corr()
    fig, ax = plt.subplots(figsize=(max(8, len(value_cols)), max(6, len(value_cols)-1)))
    mask = np.triu(np.ones_like(corr, dtype=bool))   # 上三角をマスク
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
                cmap="RdYlGn", center=0, vmin=-1, vmax=1,
                linewidths=0.5, ax=ax)
    ax.set_title("② 相関行列ヒートマップ", fontsize=14)
    plt.tight_layout()
    path = f"{save_dir}02_correlation.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"保存：{path}")

    # ③ ペアプロット ────────────────────────────
    print("\n③ ペアプロット（最大5変数）")
    cols_for_pair = value_cols[:5]
    pair_df = df[cols_for_pair].dropna()
    pair_grid = sns.pairplot(pair_df, diag_kind="kde", plot_kws={"alpha": 0.4})
    pair_grid.figure.suptitle("③ ペアプロット", y=1.02, fontsize=14)
    path = f"{save_dir}03_pairplot.png"
    pair_grid.savefig(path, dpi=120, bbox_inches="tight")
    plt.show()
    print(f"保存：{path}")

    # ④ QQプロット（正規性の確認）──────────────────
    from scipy import stats as scipy_stats
    fig, axes = plt.subplots(1, min(4, len(value_cols)),
                             figsize=(4 * min(4, len(value_cols)), 4))
    if len(value_cols) == 1:
        axes = [axes]
    for ax, col in zip(axes, value_cols[:4]):
        data = df[col].dropna()
        scipy_stats.probplot(data, dist="norm", plot=ax)
        ax.set_title(f"④ QQプロット：{col}", fontsize=10)
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path = f"{save_dir}04_qqplot.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"保存：{path}")

    return corr

corr_matrix = run_eda(df_featured, value_cols=["人口増減率", "高齢化率", "人口密度", "地価"])
```

#### EDA 追加分析（課題に応じて実施）：

```python
# ── A: 時系列分解（トレンド・季節性・残差）──────────────
from statsmodels.tsa.seasonal import seasonal_decompose

def eda_time_series(df: pd.DataFrame, value_col: str, time_col: str, freq: int = 1):
    ts = df.set_index(time_col)[value_col].dropna()
    result = seasonal_decompose(ts, model="additive", period=freq)
    result.plot()
    plt.suptitle(f"時系列分解：{value_col}", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"output/figures/05_ts_decompose_{value_col}.png", dpi=150)
    plt.show()

# ── B: 空間的自己相関（モランI統計）──────────────────
# ※ GISデータ（shapefile等）がある場合に使用
# import libpysal
# from esda.moran import Moran
# w = libpysal.weights.Queen.from_dataframe(gdf)
# moran = Moran(gdf[value_col], w)
# print(f"Moran's I = {moran.I:.3f}, p-value = {moran.p_sim:.4f}")

# ── C: 多重共線性の確認（VIF） ────────────────────
from statsmodels.stats.outliers_influence import variance_inflation_factor

def check_vif(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    X = df[feature_cols].dropna()
    vif_data = pd.DataFrame({
        "特徴量": feature_cols,
        "VIF": [variance_inflation_factor(X.values, i) for i in range(len(feature_cols))]
    }).sort_values("VIF", ascending=False)
    print("【VIF（多重共線性チェック）】\n  VIF > 10 は要注意")
    print(vif_data.to_string(index=False))
    return vif_data

vif = check_vif(df_featured, feature_cols=["高齢化率", "人口密度", "地価_log"])
```

#### EDA 後に必ず出力する「EDA サマリー」：
```
【EDA サマリー】
─────────────────────────────────────────
■ データ品質：
  - 総行数：___行、総列数：___列
  - 欠損が多い列：
  - 外れ値が疑われる列：

■ 分布の特徴：
  - 正規分布に近い変数：
  - 歪みが大きい変数（対数変換推奨）：

■ 注目すべき相関：
  - 強い正相関（r>0.7）：
  - 強い負相関（r<-0.7）：
  - 目的変数との相関が高い変数：

■ 多重共線性リスク：
  - VIF > 10 の変数：（該当なし / あり：___）

■ モデリングへの示唆：
  - 採用する説明変数の候補：
  - 前処理が必要な変数：
  - 分析上の注意点：
─────────────────────────────────────────
```

---

### ▶ STEP 11：複数モデル構築

**目的**：RQに対して複数の手法でモデルを作り、比較できる状態にする。

**先に確認すること**（詳細は `data-science-foundations` の `references/ml-validation.md`）：
- 単純な基準モデル（平均・前年同値・線形回帰）を必ず入れ、それを上回るかで評価する。
- データの分け方：時系列は時間順、同じ地域・施設が複数行あるデータはまとまりごと（`GroupKFold`）、空間データは地域のブロックで分ける。無作為に分けると、成績が実力より良く出る。
- 標準化・欠測補完・特徴量選択は `Pipeline` の中で行う（評価用データの情報を学習に混ぜない）。
- 件数が少ない（区・町丁単位で数十〜数百件）場合は、複雑なモデルより、正則化付きの線形モデルと、係数の信頼区間を優先する。

```python
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import numpy as np
import pandas as pd

# ── データ準備 ─────────────────────────────────
TARGET   = "人口増減率"          # ← RQに応じて変更
FEATURES = ["高齢化率", "人口密度", "地価_log", "駅距離_m"]  # ← EDA結果を踏まえて設定

df_model = df_featured[FEATURES + [TARGET]].dropna()
X = df_model[FEATURES]
y = df_model[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"学習：{len(X_train)}件 / テスト：{len(X_test)}件")

# ── モデル定義 ──────────────────────────────────
# 課題タイプ別にコメントアウトを解除して使用すること
models = {
    # ── 回帰モデル ──
    "線形回帰":           Pipeline([("sc", StandardScaler()), ("m", LinearRegression())]),
    "リッジ回帰":         Pipeline([("sc", StandardScaler()), ("m", Ridge(alpha=1.0))]),
    "Lasso回帰":          Pipeline([("sc", StandardScaler()), ("m", Lasso(alpha=0.1))]),
    "ランダムフォレスト":  RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
    "XGBoost":            xgb.XGBRegressor(n_estimators=200, learning_rate=0.05,
                                           random_state=42, verbosity=0),
    "勾配ブースティング":  GradientBoostingRegressor(n_estimators=200, random_state=42),
}

# ── 学習（クロスバリデーション込み）───────────────────
kf = KFold(n_splits=5, shuffle=True, random_state=42)
trained = {}
cv_results = {}

for name, model in models.items():
    # クロスバリデーション（過学習チェック）
    cv_scores = cross_val_score(model, X_train, y_train,
                                cv=kf, scoring="r2", n_jobs=-1)
    cv_results[name] = {"CV_R2_mean": cv_scores.mean(), "CV_R2_std": cv_scores.std()}
    # 全学習データで再学習
    model.fit(X_train, y_train)
    trained[name] = model
    print(f"✅ {name}：CV R² = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
```

---

### ▶ STEP 12：モデル評価・比較

**目的**：どのモデルが最も信頼できるかを客観的指標で比較する。

```python
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    mean_absolute_percentage_error
)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def evaluate_models(trained: dict,
                    X_test, y_test,
                    cv_results: dict = None,
                    save_dir: str = "output/figures/") -> pd.DataFrame:
    """
    複数モデルをテストデータで評価し、比較表と可視化を出力する。
    評価指標：RMSE（小さいほど良い）、MAE、MAPE、R²（高いほど良い）
    """
    import os
    os.makedirs(save_dir, exist_ok=True)
    results = []

    for name, model in trained.items():
        y_pred = model.predict(X_test)
        row = {
            "モデル":  name,
            "RMSE":   np.sqrt(mean_squared_error(y_test, y_pred)),
            "MAE":    mean_absolute_error(y_test, y_pred),
            "MAPE":   mean_absolute_percentage_error(y_test, y_pred),
            "R²":     r2_score(y_test, y_pred),
        }
        if cv_results and name in cv_results:
            row["CV_R²"] = cv_results[name]["CV_R2_mean"]
        results.append(row)

    df_eval = pd.DataFrame(results).set_index("モデル").round(4)

    # ── テスト R² の棒グラフ ──
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    df_eval["R²"].sort_values().plot(
        kind="barh", ax=axes[0], color="#2196F3",
        title="モデル比較：R²（高いほど良い）", xlim=(0, 1)
    )
    axes[0].axvline(0.8, color="red", linestyle="--", label="R²=0.8（目安）")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    df_eval["RMSE"].sort_values(ascending=False).plot(
        kind="barh", ax=axes[1], color="#FF9800",
        title="モデル比較：RMSE（低いほど良い）"
    )
    axes[1].grid(True, alpha=0.3)
    plt.tight_layout()
    path = f"{save_dir}06_model_comparison.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"保存：{path}")

    # ── 最良モデルの特徴量重要度 ──
    best_name = df_eval["R²"].idxmax()
    best_model = trained[best_name]
    print(f"\n最良モデル：{best_name}（R² = {df_eval.loc[best_name, 'R²']:.4f}）")

    if hasattr(best_model, "feature_importances_"):
        importances = pd.Series(
            best_model.feature_importances_, index=FEATURES
        ).sort_values(ascending=True)
        importances.plot(kind="barh", figsize=(8, 4), color="#4CAF50",
                         title=f"特徴量重要度（{best_name}）")
        plt.xlabel("重要度（0〜1）")
        plt.tight_layout()
        path = f"{save_dir}07_feature_importance.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.show()
        print(f"保存：{path}")

    print("\n【モデル比較表】")
    print(df_eval.to_string())
    return df_eval

df_eval = evaluate_models(trained, X_test, y_test, cv_results)
```

---

### ▶ STEP 13：分析・考察

**目的**：モデルの結果を「政策的言語」に翻訳する。

Claudeが以下のテンプレートで考察を生成し、ユーザーが確認・修正する。

```
【分析・考察サマリー】
─────────────────────────────────────────
■ 採用モデル・根拠：
  モデル名：
  選定理由（R²・解釈容易性・安定性のバランス）：

■ 主要な発見事実（Finding）：
  Finding 1：
  Finding 2：
  Finding 3：

■ 最も影響力の大きい要因（特徴量重要度より）：
  第1位：〇〇（重要度 xx%）→ 政策的意味：「___」
  第2位：△△（重要度 xx%）→ 政策的意味：「___」
  第3位：□□（重要度 xx%）→ 政策的意味：「___」

■ 地域差・格差の構造：

■ トレンドの方向性：
  現状放置の場合：
  介入した場合の変化可能性：

■ 分析の限界・留意点（必ず記載）：
  - データの制約（時点・範囲・精度）：
  - モデルの前提・仮定：
  - 因果関係ではなく相関関係である点（重要度・SHAPは「モデルが何を使ったか」であり、「変えれば結果が変わる」ことを示さない）：
  - 因果を言うために追加で必要な分析（差の差・回帰不連続・合成コントロール等。`data-science-foundations` の因果推論）：
  - データが語っていないこと：
─────────────────────────────────────────
```
