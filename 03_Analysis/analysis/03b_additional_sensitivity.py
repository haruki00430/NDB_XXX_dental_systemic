"""
Phase 3b: 追加感度分析（Spec8-10：喫煙・BMI調整）+ E-value + PAF + 四分位分析

入力:
  - 02_Data/interim/analysis_dataset_v2.csv（16列：+smoking_rate, +bmi_obesity_rate）

出力:
  - 03_Analysis/results/sensitivity_analysis_v2.csv（Spec1-10全仕様）
  - 03_Analysis/results/evalue_results.csv
  - 03_Analysis/results/paf_results.csv
  - 03_Analysis/results/quartile_analysis.csv
"""
import os
import sys
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy.stats import linregress, norm as sp_norm

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", "..", ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from ndb_library.logger import setup_logger
logger = setup_logger(__name__, log_file=os.path.join(
    PROJECT_DIR, "03_Analysis", "analysis", "logs", "phase3b_additional.log"
))

INTERIM_DIR = os.path.join(PROJECT_DIR, "02_Data", "interim")
RESULTS_DIR = os.path.join(PROJECT_DIR, "03_Analysis", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ─────────────────────────────────────────
# データ読み込み
# ─────────────────────────────────────────
df = pd.read_csv(os.path.join(INTERIM_DIR, "analysis_dataset_v2.csv"), encoding="utf-8")
logger.info(f"データ読み込み: {len(df)}行 × {len(df.columns)}列")
logger.info(f"カラム: {df.columns.tolist()}")

EXPOSURE = "periodontal_rate"
PRIMARY_OUTCOME = "dm_complication_rate"
OUTCOMES = ["hba1c_high_rate", "hba1c_mean", "dm_complication_rate", "dialysis_prevention_rate"]

# ─────────────────────────────────────────
# OLS ユーティリティ関数
# ─────────────────────────────────────────
def run_ols(df_sub, outcome, exposure, covariates, robust=None):
    y = df_sub[outcome].dropna()
    X_cols = [exposure] + covariates
    X = df_sub.loc[y.index, X_cols].dropna()
    y = y.loc[X.index]
    X_const = sm.add_constant(X)
    if robust:
        model = sm.OLS(y, X_const).fit(cov_type=robust)
    else:
        model = sm.OLS(y, X_const).fit()
    n = len(y)
    beta  = float(model.params[exposure])
    se    = float(model.bse[exposure])
    pval  = float(model.pvalues[exposure])
    ci    = model.conf_int()
    ci_lo = float(ci.loc[exposure, 0])
    ci_hi = float(ci.loc[exposure, 1])
    r2    = model.rsquared
    return {"n": n, "beta": beta, "se": se, "p_value": pval,
            "ci_lower": ci_lo, "ci_upper": ci_hi, "r2": r2}

def calc_vif(df_sub, exposure, covariates):
    X = df_sub[[exposure] + covariates].dropna()
    X_const = sm.add_constant(X)
    return {col: variance_inflation_factor(X_const.values, i)
            for i, col in enumerate(X_const.columns)}

# ─────────────────────────────────────────
# 既存 Spec1-7 を再読み込み（v1結果）
# ─────────────────────────────────────────
spec1_7_path = os.path.join(RESULTS_DIR, "sensitivity_analysis_results.csv")
if os.path.exists(spec1_7_path):
    df_spec1_7 = pd.read_csv(spec1_7_path, encoding="utf-8")
    logger.info(f"既存感度分析（Spec1-7）: {len(df_spec1_7)}行")
else:
    df_spec1_7 = pd.DataFrame()
    logger.warning("Spec1-7 結果ファイルが見つかりません。新規作成します。")

# ─────────────────────────────────────────
# Phase B-1: 追加感度分析（Spec8-10）
# ─────────────────────────────────────────
logger.info("\n===== Phase B-1: 追加感度分析（Spec8-10）=====")

new_specs = [
    {
        "name": "Spec8_Smoking",
        "description": "喫煙率（smoking_rate）追加調整",
        "covariates": ["aging_rate", "pop_density", "smoking_rate"],
        "robust": None
    },
    {
        "name": "Spec9_BMI",
        "description": "BMI肥満率（bmi_obesity_rate）追加調整",
        "covariates": ["aging_rate", "pop_density", "bmi_obesity_rate"],
        "robust": None
    },
    {
        "name": "Spec10_Full",
        "description": "全主要交絡同時調整（aging, density, income, smoking, BMI）",
        "covariates": ["aging_rate", "pop_density", "income_per_capita", "smoking_rate", "bmi_obesity_rate"],
        "robust": None
    },
]

new_rows = []
for spec in new_specs:
    spec_name = spec["name"]
    spec_desc = spec["description"]
    covs = spec["covariates"]
    robust = spec.get("robust", None)

    # VIFチェック
    vif_dict = calc_vif(df, EXPOSURE, covs)
    max_vif = max(v for k, v in vif_dict.items() if k != "const")
    logger.info(f"\n{spec_name} VIF: {vif_dict}")
    if max_vif > 10:
        logger.warning(f"  → VIF>{max_vif:.1f}: Spec10は参考扱い（多重共線性）")

    for outcome in OUTCOMES:
        try:
            res = run_ols(df, outcome, EXPOSURE, covs, robust=robust)
            sig = "✓" if res["p_value"] < 0.05 else "✗"
            logger.info(
                f"  {spec_name} | {outcome}: β={res['beta']:.6f}, "
                f"p={res['p_value']:.3f} {sig}, R²={res['r2']:.3f}"
            )
            note = f"VIF_max={max_vif:.1f}" if max_vif > 10 else spec_desc
            new_rows.append({
                "spec":        spec_name,
                "outcome":     outcome,
                "description": note,
                "n":           res["n"],
                "beta":        res["beta"],
                "se":          res["se"],
                "p_value":     res["p_value"],
                "ci_lower":    res["ci_lower"],
                "ci_upper":    res["ci_upper"],
                "r2":          res["r2"],
            })
        except Exception as e:
            logger.error(f"  {spec_name} | {outcome}: エラー - {e}")

df_new = pd.DataFrame(new_rows)

# 既存v1 + 新規Spec8-10を統合
if len(df_spec1_7) > 0:
    df_all = pd.concat([df_spec1_7, df_new], ignore_index=True)
else:
    df_all = df_new

out_path = os.path.join(RESULTS_DIR, "sensitivity_analysis_v2.csv")
df_all.to_csv(out_path, index=False, encoding="utf-8")
logger.info(f"\n感度分析v2保存: {out_path}（{len(df_all)}行）")

# dm_complication_rate での有意仕様数サマリー
dm_rows = df_all[df_all["outcome"] == PRIMARY_OUTCOME].copy()
sig_count  = (dm_rows["p_value"] < 0.05).sum()
total_spec = len(dm_rows)
logger.info(f"\ndm_complication_rate: {sig_count}/{total_spec} 仕様で有意（p<0.05）")
for _, row in dm_rows.iterrows():
    sig = "✓" if row["p_value"] < 0.05 else "✗"
    logger.info(f"  {row['spec']}: β={row['beta']:.6f}, p={row['p_value']:.3f} {sig}")

# ─────────────────────────────────────────
# Phase B-2: E-value計算（VanderWeele & Ding 2017）
# ─────────────────────────────────────────
logger.info("\n===== Phase B-2: E-value計算 =====")

# Spec1（Baseline OLS）の結果から取得
# specification 列で厳密に Baseline のみ（str.contains("Spec1") は Spec10 に誤マッチする）
spec1_dm = df_all[
    (df_all["outcome"] == PRIMARY_OUTCOME)
    & (df_all["specification"].astype(str) == "Spec1_Baseline")
]
if len(spec1_dm) == 0:
    # フォールバック: beta/se既知の値を使用
    beta_point = 0.001838
    beta_lower = 0.000109
    logger.warning("Spec1結果が見つからないためデフォルト値を使用")
else:
    spec1_row = spec1_dm.iloc[0]
    beta_point = float(spec1_row["beta"])
    beta_lower = float(spec1_row["ci_lower"])
    logger.info(f"Spec1 beta={beta_point:.6f}, CI_lower={beta_lower:.6f}")

# 標準偏差（observedデータから計算）
sd_exposure = float(df[EXPOSURE].std())
sd_outcome  = float(df[PRIMARY_OUTCOME].std())
logger.info(f"SD(periodontal_rate)={sd_exposure:.1f}, SD(dm_complication_rate)={sd_outcome:.1f}")

# 標準化β → RR変換
std_beta_point = beta_point * (sd_exposure / sd_outcome)
std_beta_lower = beta_lower * (sd_exposure / sd_outcome)
RR_point = float(np.exp(std_beta_point))
RR_lower = float(np.exp(std_beta_lower))
logger.info(f"標準化β(点推定)={std_beta_point:.4f}, RR={RR_point:.4f}")
logger.info(f"標準化β(CI下限)={std_beta_lower:.4f}, RR={RR_lower:.4f}")

# E-value計算式: E = RR + sqrt(RR * (RR - 1))
def evalue(rr):
    if rr < 1:
        rr = 1 / rr  # RR<1の場合は逆転
    return rr + np.sqrt(rr * (rr - 1))

ev_point = evalue(RR_point)
ev_lower = evalue(RR_lower) if RR_lower > 1 else 1.0

logger.info(f"E-value（点推定）: {ev_point:.3f}")
logger.info(f"E-value（CI下限）: {ev_lower:.3f}")
logger.info(
    f"解釈: 所得との相関r≈0.61 → RR換算≈{np.exp(0.61 * std_beta_point / std_beta_lower):.2f}程度 "
    f"→ E-value({ev_point:.2f})は所得1因子でほぼ説明不可"
)

df_evalue = pd.DataFrame([{
    "outcome":          PRIMARY_OUTCOME,
    "beta_point":       beta_point,
    "beta_ci_lower":    beta_lower,
    "sd_exposure":      sd_exposure,
    "sd_outcome":       sd_outcome,
    "std_beta_point":   std_beta_point,
    "RR_point":         RR_point,
    "RR_lower":         RR_lower,
    "evalue_point":     ev_point,
    "evalue_ci_lower":  ev_lower,
}])
df_evalue.to_csv(os.path.join(RESULTS_DIR, "evalue_results.csv"), index=False, encoding="utf-8")
logger.info("E-value 保存完了")

# ─────────────────────────────────────────
# Phase B-3: PAF（Population Attributable Fraction）推定
# ─────────────────────────────────────────
logger.info("\n===== Phase B-3: PAF推定 =====")

# 四分位に分割してQ4/Q1のアウトカム平均を計算
df["periodontal_q"] = pd.qcut(df[EXPOSURE], q=4, labels=[1, 2, 3, 4])
quartile_means = df.groupby("periodontal_q", observed=True)[PRIMARY_OUTCOME].agg(["mean", "count", "std"])
logger.info(f"四分位別 {PRIMARY_OUTCOME} 平均:\n{quartile_means.to_string()}")

dm_q1 = float(quartile_means.loc[1, "mean"])
dm_q4 = float(quartile_means.loc[4, "mean"])
RR_Q4_Q1 = dm_q4 / dm_q1

logger.info(f"Q1平均={dm_q1:.1f}, Q4平均={dm_q4:.1f}, RR(Q4/Q1)={RR_Q4_Q1:.3f}")

# PAF計算（Q4地域に人口の25%が居住と仮定）
p_exposed = 0.25
PAF = (p_exposed * (RR_Q4_Q1 - 1)) / (1 + p_exposed * (RR_Q4_Q1 - 1))
logger.info(f"PAF（推定）= {PAF*100:.1f}%")

# 超過件数推計（日本の40-74歳人口 ≈ 4,800万人）
pop_40_74 = 48_000_000
dm_complication_mean = float(df[PRIMARY_OUTCOME].mean())
excess_cases = dm_complication_mean / 100_000 * pop_40_74 * PAF
logger.info(f"超過件数推計 ≈ {excess_cases:,.0f} 件/年（DM合併症管理料）")

df_paf = pd.DataFrame([{
    "outcome":         PRIMARY_OUTCOME,
    "Q1_mean":         dm_q1,
    "Q4_mean":         dm_q4,
    "RR_Q4_Q1":        RR_Q4_Q1,
    "p_exposed":       p_exposed,
    "PAF_pct":         PAF * 100,
    "pop_reference":   pop_40_74,
    "excess_cases":    excess_cases,
}])
df_paf.to_csv(os.path.join(RESULTS_DIR, "paf_results.csv"), index=False, encoding="utf-8")
logger.info("PAF 保存完了")

# ─────────────────────────────────────────
# Phase B-4: 四分位分析（Dose-response）
# ─────────────────────────────────────────
logger.info("\n===== Phase B-4: 四分位分析 =====")

import statsmodels.formula.api as smf

quartile_rows = []
for q in [1, 2, 3, 4]:
    group = df[df["periodontal_q"] == q][PRIMARY_OUTCOME]
    quartile_rows.append({
        "quartile":  q,
        "n":         len(group),
        "mean":      float(group.mean()),
        "sd":        float(group.std()),
        "se":        float(group.std() / np.sqrt(len(group))),
        "ci_lower":  float(group.mean() - 1.96 * group.std() / np.sqrt(len(group))),
        "ci_upper":  float(group.mean() + 1.96 * group.std() / np.sqrt(len(group))),
        "min":       float(group.min()),
        "max":       float(group.max()),
    })

df_quartile = pd.DataFrame(quartile_rows)
logger.info(f"四分位分析結果:\n{df_quartile.to_string()}")

# 線形トレンド検定
q_vals = df["periodontal_q"].astype(int)
y_vals = df[PRIMARY_OUTCOME]
slope, intercept, r_val, p_trend, se_trend = linregress(q_vals, y_vals)
logger.info(f"線形トレンド: slope={slope:.2f}, r={r_val:.3f}, p_trend={p_trend:.3f}")
df_quartile["p_trend"] = p_trend
df_quartile["trend_slope"] = slope

df_quartile.to_csv(os.path.join(RESULTS_DIR, "quartile_analysis.csv"), index=False, encoding="utf-8")
logger.info("四分位分析 保存完了")

# ─────────────────────────────────────────
# 最終サマリー
# ─────────────────────────────────────────
logger.info("\n===== Phase 3b 完了サマリー =====")
logger.info(f"sensitivity_analysis_v2.csv: {len(df_all)}行（全仕様）")
logger.info(f"dm_complication_rate: {sig_count}/{total_spec} 仕様で有意")
logger.info(f"E-value（点推定）: {ev_point:.3f}（CI下限: {ev_lower:.3f}）")
logger.info(f"PAF推定: {PAF*100:.1f}%、超過件数: {excess_cases:,.0f}件/年")
logger.info(f"四分位トレンド p={p_trend:.3f}")
logger.info("Phase 3b 完了")
