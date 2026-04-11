"""
Phase 5: 所得の正式媒介分析

パス:  periodontal_rate (X) → income_per_capita (M) → dm_complication_rate (Y)
共変量: aging_rate, pop_density

入力: 02_Data/interim/analysis_dataset_v2.csv
出力:
  - 03_Analysis/results/mediation_results.csv
  - 03_Analysis/results/mediation_report.md
"""
import os
import sys
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from statsmodels.stats.mediation import Mediation

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", "..", ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from ndb_library.logger import setup_logger
logger = setup_logger(__name__, log_file=os.path.join(
    PROJECT_DIR, "03_Analysis", "analysis", "logs", "phase5_mediation.log"
))

INTERIM_DIR = os.path.join(PROJECT_DIR, "02_Data", "interim")
RESULTS_DIR = os.path.join(PROJECT_DIR, "03_Analysis", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

np.random.seed(42)

# ─────────────────────────────────────────
# データ読み込み・スケーリング
# ─────────────────────────────────────────
df = pd.read_csv(os.path.join(INTERIM_DIR, "analysis_dataset_v2.csv"), encoding="utf-8")
logger.info(f"データ読み込み: {len(df)}行 × {len(df.columns)}列")

# 数値安定化のためスケーリング（係数の解釈しやすさのため）
df["periodontal_scaled"] = df["periodontal_rate"] / 10000   # 1万件/10万人単位
df["income_scaled"]      = df["income_per_capita"] / 100    # 100万円単位
df["dm_scaled"]          = df["dm_complication_rate"]       # そのまま（件/10万人）

logger.info(f"periodontal_scaled: mean={df['periodontal_scaled'].mean():.3f}, SD={df['periodontal_scaled'].std():.3f}")
logger.info(f"income_scaled:      mean={df['income_scaled'].mean():.3f}, SD={df['income_scaled'].std():.3f}")
logger.info(f"dm_scaled:          mean={df['dm_scaled'].mean():.1f}, SD={df['dm_scaled'].std():.1f}")

# ─────────────────────────────────────────
# ステップ 1: 単純相関の確認
# ─────────────────────────────────────────
r_x_m = float(df["periodontal_scaled"].corr(df["income_scaled"]))
r_m_y = float(df["income_scaled"].corr(df["dm_scaled"]))
r_x_y = float(df["periodontal_scaled"].corr(df["dm_scaled"]))
logger.info(f"単純相関: r(X,M)={r_x_m:.3f}, r(M,Y)={r_m_y:.3f}, r(X,Y)={r_x_y:.3f}")
logger.info("注: r(X,M)>0かつr(M,Y)方向を確認（媒介の前提条件）")

# ─────────────────────────────────────────
# ステップ 2: 媒介モデルの定義
# ─────────────────────────────────────────
# Mediator model: income_scaled ~ periodontal_scaled + aging_rate + pop_density
mediator_model = smf.ols(
    "income_scaled ~ periodontal_scaled + aging_rate + pop_density",
    data=df
)

# Outcome model: dm_scaled ~ periodontal_scaled + income_scaled + aging_rate + pop_density
outcome_model = smf.ols(
    "dm_scaled ~ periodontal_scaled + income_scaled + aging_rate + pop_density",
    data=df
)

# モデルフィットの確認（ログ用）
m_fit = mediator_model.fit()
o_fit = outcome_model.fit()
logger.info(f"Mediator model: R2={m_fit.rsquared:.3f}, "
            f"coef(periodontal)={m_fit.params['periodontal_scaled']:.4f}, "
            f"p={m_fit.pvalues['periodontal_scaled']:.3f}")
logger.info(f"Outcome model:  R2={o_fit.rsquared:.3f}, "
            f"coef(periodontal)={o_fit.params['periodontal_scaled']:.4f}, "
            f"p={o_fit.pvalues['periodontal_scaled']:.3f}, "
            f"coef(income)={o_fit.params['income_scaled']:.4f}, "
            f"p={o_fit.pvalues['income_scaled']:.3f}")

# ─────────────────────────────────────────
# ステップ 3: Mediation分析（Bootstrap 1,000回）
# ─────────────────────────────────────────
logger.info("Mediation 分析開始（Bootstrap n=1000）...")
med = Mediation(
    outcome_model=outcome_model,
    mediator_model=mediator_model,
    exposure="periodontal_scaled",
    mediator="income_scaled"
)

np.random.seed(42)
med_result = med.fit(n_rep=1000, method="bootstrap")
summary = med_result.summary()
logger.info(f"Mediation Summary:\n{summary.to_string()}")

# ─────────────────────────────────────────
# ステップ 4: 結果の抽出
# ─────────────────────────────────────────
try:
    rows = summary.tables[0] if hasattr(summary, 'tables') else summary
    # MediationResults.summary() は SimpleTable を返す
    # フォールバック: DataFrameとして扱う
    if hasattr(summary, 'as_csv'):
        import io
        df_sum = pd.read_csv(io.StringIO(summary.as_csv()))
    else:
        df_sum = pd.DataFrame(summary)
except Exception as e:
    logger.warning(f"サマリー変換エラー: {e}")
    df_sum = None

# Bootstrap分布から直接計算
acme_arr  = np.array(med_result.ACME_mean)  if hasattr(med_result, 'ACME_mean')  else np.nan
ade_arr   = np.array(med_result.ADE_mean)   if hasattr(med_result, 'ADE_mean')   else np.nan
total_arr = np.array(med_result.total_effect) if hasattr(med_result, 'total_effect') else np.nan

# get_boot_ci から信頼区間取得
try:
    acme_ci  = med_result.summary().tables[0]
    # summary()から読み取る方が確実
    logger.info("summary() からの信頼区間取得を試みます")
except:
    pass

# より確実な方法：summary テーブルのパース
try:
    summary_str = str(summary)
    logger.info(f"Summary raw text:\n{summary_str}")
except Exception as e:
    logger.warning(f"Summary文字列取得エラー: {e}")

# ─────────────────────────────────────────
# ステップ 5: 結果をDataFrameに整理して保存
# ─────────────────────────────────────────
# summary()の戻り値からDataFrameに変換
try:
    # statsmodels Mediation.summary()はSimpleTable
    # as_html()→parseが確実
    from io import StringIO
    html_str = summary.as_html()
    tables = pd.read_html(StringIO(html_str))
    df_med = tables[0]
    logger.info(f"Mediation table:\n{df_med.to_string()}")
except Exception as e:
    logger.warning(f"HTML parse failed: {e}")
    # 手動構築のフォールバック
    # Total effect = Spec1 Baseline OLS のβ（スケール変換後）
    beta_total = float(o_fit.params["periodontal_scaled"]) + float(m_fit.params["periodontal_scaled"]) * float(o_fit.params["income_scaled"])
    df_med = pd.DataFrame([{
        "effect": "Total_Effect_approx",
        "estimate": beta_total,
        "note": "approx from model coefficients"
    }])

df_med.to_csv(os.path.join(RESULTS_DIR, "mediation_results.csv"), index=False, encoding="utf-8")
logger.info("mediation_results.csv 保存完了")

# ─────────────────────────────────────────
# ステップ 6: 解釈レポート（Markdown）
# ─────────────────────────────────────────
# モデル係数から媒介効果を計算（Baron-Kenny approach）
a_coef  = float(m_fit.params["periodontal_scaled"])   # X → M
b_coef  = float(o_fit.params["income_scaled"])        # M → Y (Xも含むモデル)
c_coef  = float(o_fit.params["periodontal_scaled"])   # X → Y (Mを含む、ADE)

# total effect（単純OLS）
total_model = smf.ols("dm_scaled ~ periodontal_scaled + aging_rate + pop_density", data=df).fit()
c_total     = float(total_model.params["periodontal_scaled"])  # X → Y (Mなし、Total)
p_total     = float(total_model.pvalues["periodontal_scaled"])

indirect_bk = a_coef * b_coef  # a×b = ACME (Baron-Kenny)
prop_med    = indirect_bk / c_total if abs(c_total) > 1e-10 else float("nan")

logger.info(f"Baron-Kenny: a={a_coef:.4f}, b={b_coef:.4f}, c'={c_coef:.4f}, c={c_total:.4f}")
logger.info(f"間接効果(a*b)={indirect_bk:.4f}, 媒介割合={prop_med*100:.1f}%")
logger.info(f"Total effect (c): beta={c_total:.4f}, p={p_total:.3f}")
logger.info(f"ADE (c'): beta={c_coef:.4f}, p={o_fit.pvalues['periodontal_scaled']:.3f}")
logger.info(f"Income coef (b): beta={b_coef:.4f}, p={o_fit.pvalues['income_scaled']:.3f}")

# シナリオ判定
acme_p = None
try:
    # summary tableからACMEのp値を抽出
    summary_str = str(summary)
    # ACMEの行を探す
    for line in summary_str.split('\n'):
        if 'ACME' in line and 'Prop.' not in line:
            logger.info(f"ACME行: {line}")
except:
    pass

# シナリオA/Bの判定（Baron-Kenny 媒介割合に基づく）
if abs(prop_med) > 0.20 and a_coef * b_coef * c_total > 0:
    scenario = "A"
    scenario_note = "所得はpartial mediator（媒介割合>20%）。ADE（直接効果）が残存すればSpec7は過調整"
else:
    scenario = "B"
    scenario_note = "所得は交絡因子として機能（媒介証拠不十分）。Spec7は保守的推定として解釈すべき"

logger.info(f"媒介分析シナリオ: {scenario} - {scenario_note}")

# Markdownレポート生成
report_lines = [
    "# 所得媒介分析レポート（Baron-Kenny + Bootstrap）\n",
    f"**解析日**: 2026-04-07  \n",
    f"**曝露**: periodontal_rate（/10万人、スケール: ÷10000）  \n",
    f"**媒介変数**: income_per_capita（スケール: ÷100）  \n",
    f"**アウトカム**: dm_complication_rate（件/10万人）  \n",
    f"**共変量**: aging_rate, pop_density  \n\n",
    "## パス係数（Baron-Kenny）\n\n",
    f"| パス | 係数 | p値 |\n",
    f"|-----|------|-----|\n",
    f"| a: periodontal → income | {a_coef:.4f} | {m_fit.pvalues['periodontal_scaled']:.3f} |\n",
    f"| b: income → dm_comp（直接） | {b_coef:.4f} | {o_fit.pvalues['income_scaled']:.3f} |\n",
    f"| c: Total effect | {c_total:.4f} | {p_total:.3f} |\n",
    f"| c': ADE（所得調整後） | {c_coef:.4f} | {o_fit.pvalues['periodontal_scaled']:.3f} |\n\n",
    "## 媒介効果（Baron-Kenny）\n\n",
    f"- **間接効果（a×b）**: {indirect_bk:.4f}\n",
    f"- **媒介割合**: {prop_med*100:.1f}%\n\n",
    f"## 解釈（シナリオ{scenario}）\n\n",
    f"{scenario_note}\n\n",
    "## 論文記載文案（英語）\n\n",
]

if scenario == "A":
    report_lines.append(
        "Formal mediation analysis indicated that income_per_capita partially mediated "
        "the association between periodontal_rate and dm_complication_rate "
        f"(indirect effect via Baron-Kenny: {indirect_bk:.3f}; "
        f"proportion mediated: {prop_med*100:.1f}%). "
        "The direct effect (ADE) remained in the same direction "
        f"(beta = {c_coef:.4f}, p = {o_fit.pvalues['periodontal_scaled']:.3f}), "
        "suggesting that income acts as a partial mediator rather than a pure confounder. "
        "The attenuation observed in Spec7 (full income adjustment) may therefore reflect "
        "partial over-adjustment rather than pure confounding.\n"
    )
else:
    report_lines.append(
        "Formal mediation analysis did not provide strong evidence that income_per_capita "
        "mediated the association between periodontal_rate and dm_complication_rate "
        f"(Baron-Kenny indirect effect: {indirect_bk:.3f}; "
        f"proportion mediated: {prop_med*100:.1f}%). "
        "Income appears to function primarily as a measured confounder in this dataset. "
        "The attenuation in Spec7 (full income adjustment) is therefore interpreted as "
        "a conservative sensitivity analysis, and the primary estimate (Spec1) "
        "remains the most appropriate reference. "
        "Given the small sample size (N=47), formal mediation analysis was underpowered "
        "to detect indirect effects and should be interpreted with caution.\n"
    )

report_path = os.path.join(RESULTS_DIR, "mediation_report.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.writelines(report_lines)

logger.info(f"Mediation report 保存: {report_path}")
logger.info("Phase 5 完了")
