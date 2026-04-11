"""
Phase 4b: 追加図3枚

Figure 6: 四分位別 dm_complication_rate バープロット（Q1基準、95%CI付き）
Figure 7: 感度分析拡張 Forest plot（Spec1-10全仕様）
Figure 8: E-value可視化

入力:
  - 03_Analysis/results/quartile_analysis.csv
  - 03_Analysis/results/sensitivity_analysis_v2.csv
  - 03_Analysis/results/evalue_results.csv

出力:
  - results/figures/quartile_dm_complication.png
  - results/figures/forest_plot_dm_complication_v2.png
  - results/figures/evalue_visualization.png
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import yaml

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", "..", ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from ndb_library.logger import setup_logger

logger = setup_logger(
    __name__,
    log_file=os.path.join(PROJECT_DIR, "03_Analysis", "analysis", "logs", "phase4b_figures.log"),
)

with open(os.path.join(PROJECT_DIR, "config", "config.yaml"), "r", encoding="utf-8") as f:
    _cfg = yaml.safe_load(f)

RESULTS_DIR = os.path.join(PROJECT_DIR, _cfg["output"]["results_dir"])
FIGURES_DIR = os.path.join(PROJECT_DIR, _cfg["output"]["figures_dir"])
os.makedirs(FIGURES_DIR, exist_ok=True)

# ─────────────────────────────────────────
# Figure 6: 四分位別バープロット
# ─────────────────────────────────────────
logger.info("Figure 6: 四分位別バープロット作成")
df_q = pd.read_csv(os.path.join(RESULTS_DIR, "quartile_analysis.csv"), encoding="utf-8")

fig, ax = plt.subplots(figsize=(7, 5))

q_labels = ["Q1\n(lowest)", "Q2", "Q3", "Q4\n(highest)"]
means    = df_q["mean"].values
ci_lo    = df_q["ci_lower"].values
ci_hi    = df_q["ci_upper"].values
err_lo   = means - ci_lo
err_hi   = ci_hi - means

colors = ["#4575b4", "#74add1", "#f4a582", "#d73027"]
bars = ax.bar(range(4), means, color=colors, width=0.55, edgecolor="black", linewidth=0.8)
ax.errorbar(range(4), means, yerr=[err_lo, err_hi],
            fmt="none", color="black", capsize=5, linewidth=1.2, capthick=1.2)

ax.set_xticks(range(4))
ax.set_xticklabels(q_labels, fontsize=11)
ax.set_xlabel("Quartile of periodontal disease claim rate", fontsize=12)
ax.set_ylabel("Diabetic complication management rate\n(claims per 100,000 population)", fontsize=12)
ax.set_title(
    "Diabetic complication management rate by quartile of periodontal claim rate",
    fontsize=12,
    fontweight="bold",
)

# Q1の値を基準線として表示
q1_mean = means[0]
ax.axhline(y=q1_mean, color="gray", linestyle="--", linewidth=1, alpha=0.7, label=f"Q1 baseline = {q1_mean:.1f}")

# 各棒に値を表示
for i, (bar, m) in enumerate(zip(bars, means)):
    ax.text(bar.get_x() + bar.get_width()/2, m + 10, f"{m:.1f}", ha="center", va="bottom", fontsize=10)

p_trend = float(df_q["p_trend"].iloc[0])
slope   = float(df_q["trend_slope"].iloc[0])
ax.text(0.98, 0.05, f"Trend: p = {p_trend:.3f}", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=10, color="gray",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))

ax.set_ylim(0, max(ci_hi) * 1.15)
ax.legend(fontsize=9, loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
out_path = os.path.join(FIGURES_DIR, "quartile_dm_complication.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()
logger.info(f"Figure 6 保存: {out_path}")

# ─────────────────────────────────────────
# Figure 7: 拡張 Forest plot（Spec1-10全仕様）
# ─────────────────────────────────────────
logger.info("Figure 7: 拡張 Forest plot 作成")
df_sa = pd.read_csv(os.path.join(RESULTS_DIR, "sensitivity_analysis_v2.csv"), encoding="utf-8")

# dm_complication_rate のみ
df_dm = df_sa[df_sa["outcome"] == "dm_complication_rate"].copy().reset_index(drop=True)

# spec列がNaN（旧形式）の行にラベルを補完
spec_labels_default = [
    "Spec1: Baseline OLS",
    "Spec2: HC3 Robust SE",
    "Spec3: Outlier removed",
    "Spec4: Urban excl.",
    "Spec5: Log-transformed",
    "Spec6: Aging only",
    "Spec7: + Income",
]
for i, row in df_dm.iterrows():
    if pd.isna(row.get("spec", None)) or str(row.get("spec", "")).strip() in ["nan", ""]:
        if i < len(spec_labels_default):
            df_dm.at[i, "spec"] = spec_labels_default[i]
        else:
            df_dm.at[i, "spec"] = f"Spec{i+1}"

# Spec8_LM_ns（NaN行）は除外
df_dm = df_dm.dropna(subset=["beta"]).reset_index(drop=True)

# ラベルの整形
label_map = {
    "Spec1_Baseline": "Spec1: Baseline OLS",
    "Spec2_HC3": "Spec2: HC3 Robust SE",
    "Spec3_OutlierRemoved": "Spec3: Outlier removed",
    "Spec4_UrbanExcluded": "Spec4: Urban excl.",
    "Spec5_LogTransformed": "Spec5: Log-transformed",
    "Spec6_AgingOnly": "Spec6: Aging only",
    "Spec7_IncomeAdjusted": "Spec7: + Income",
    "Spec8_Smoking": "Spec8: + Smoking rate",
    "Spec9_BMI": "Spec9: + BMI obesity",
    "Spec10_Full": "Spec10: Full adjustment",
}
df_dm["label"] = df_dm["spec"].map(label_map).fillna(df_dm["spec"])

# 色分け: 有意→赤、非有意→灰
colors_fp = ["#d73027" if p < 0.05 else "#aaaaaa" for p in df_dm["p_value"]]

n_specs = len(df_dm)
fig_h = max(5, n_specs * 0.55 + 1.5)
fig, ax = plt.subplots(figsize=(9, fig_h))

y_pos = list(range(n_specs - 1, -1, -1))  # 上から下
for idx, (i, row) in enumerate(df_dm.iterrows()):
    y = y_pos[idx]
    beta  = row["beta"]
    ci_lo = row["ci_lower"]
    ci_hi = row["ci_upper"]
    pval  = row["p_value"]
    color = colors_fp[idx]

    ax.plot([ci_lo, ci_hi], [y, y], color=color, linewidth=1.5)
    ax.plot(beta, y, "D", color=color, markersize=7, zorder=5)

    sig_str = f"p={pval:.3f}*" if pval < 0.05 else f"p={pval:.3f}"
    ax.text(ax.get_xlim()[1] if ax.get_xlim()[1] > 0 else 0.005,
            y, f"  {sig_str}", va="center", fontsize=8, color=color)

ax.axvline(x=0, color="black", linestyle="--", linewidth=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(df_dm["label"].tolist(), fontsize=9)
ax.set_xlabel("Regression Coefficient (β) for periodontal_rate\n→ dm_complication_rate", fontsize=10)
ax.set_title(
    "Sensitivity analysis: all specifications (forest plot)\n(dm_complication_rate, N=47)",
    fontsize=11,
    fontweight="bold",
)

# 凡例
red_patch  = mpatches.Patch(color="#d73027", label="p < 0.05")
gray_patch = mpatches.Patch(color="#aaaaaa", label="p ≥ 0.05")
ax.legend(handles=[red_patch, gray_patch], fontsize=9, loc="lower right")

sig_count = (df_dm["p_value"] < 0.05).sum()
total_count = len(df_dm)
ax.text(
    0.02,
    0.02,
    f"Significant specifications: {sig_count}/{total_count}",
    transform=ax.transAxes,
    fontsize=9,
    color="darkred",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()

out_path = os.path.join(FIGURES_DIR, "forest_plot_dm_complication_v2.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()
logger.info(f"Figure 7 保存: {out_path}")

# ─────────────────────────────────────────
# Figure 8: E-value 可視化
# ─────────────────────────────────────────
logger.info("Figure 8: E-value 可視化")
df_ev = pd.read_csv(os.path.join(RESULTS_DIR, "evalue_results.csv"), encoding="utf-8")

# 正しいSpec1の値で再計算（β=0.001838, CI_lower=0.000109）
beta_spec1 = 0.001838
ci_lower_spec1 = 0.000109
sd_exp = float(df_ev["sd_exposure"].iloc[0])
sd_out = float(df_ev["sd_outcome"].iloc[0])

std_b_pt = beta_spec1 * (sd_exp / sd_out)
std_b_lo = ci_lower_spec1 * (sd_exp / sd_out)
RR_pt = np.exp(std_b_pt)
RR_lo = np.exp(std_b_lo)

def evalue(rr):
    if rr < 1:
        rr = 1 / rr
    return rr + np.sqrt(rr * (rr - 1))

ev_pt = evalue(RR_pt)
ev_lo = evalue(RR_lo)

logger.info(f"E-value（正しい計算）: 点推定={ev_pt:.3f}, CI下限={ev_lo:.3f}")

fig, ax = plt.subplots(figsize=(8, 5))

# E-value曲線を描画
rr_vals = np.linspace(1.001, 5, 300)
ev_curve = [evalue(r) for r in rr_vals]
ax.plot(rr_vals, ev_curve, "b-", linewidth=2, label="E-value curve")

# 点推定のE-value
ax.axvline(x=RR_pt, color="#d73027", linestyle="--", linewidth=1.5,
           label=f"RR (point estimate) = {RR_pt:.2f}")
ax.axvline(x=RR_lo, color="#f4a582", linestyle="--", linewidth=1.5,
           label=f"RR (CI lower) = {RR_lo:.2f}")

# E-value の位置をマーク
ax.axhline(y=ev_pt, color="#d73027", linestyle=":", linewidth=1, alpha=0.7)
ax.axhline(y=ev_lo, color="#f4a582", linestyle=":", linewidth=1, alpha=0.7)

# 既知交絡（所得 r≈0.61）のRR推定
rr_income = np.exp(0.61 * std_b_pt / std_b_lo) if std_b_lo > 0 else 1.5
ax.axvline(x=rr_income, color="#2166ac", linestyle="-.", linewidth=1.5,
           alpha=0.8, label=f"Income RR (approx) = {rr_income:.2f}")

ax.scatter([RR_pt], [ev_pt], color="#d73027", s=80, zorder=10)
ax.scatter([RR_lo], [ev_lo], color="#f4a582", s=80, zorder=10)

ax.annotate(f"E-value = {ev_pt:.2f}", xy=(RR_pt, ev_pt),
            xytext=(RR_pt + 0.3, ev_pt + 0.2),
            fontsize=10, color="#d73027",
            arrowprops=dict(arrowstyle="->", color="#d73027"))
ax.annotate(f"E-value\n(CI lower) = {ev_lo:.2f}", xy=(RR_lo, ev_lo),
            xytext=(RR_lo + 0.3, ev_lo + 0.3),
            fontsize=9, color="#f4a582",
            arrowprops=dict(arrowstyle="->", color="#f4a582"))

ax.set_xlim(1, 4.5)
ax.set_ylim(1, ax.get_ylim()[1] if ax.get_ylim()[1] > ev_pt * 1.3 else ev_pt * 1.5)
ax.set_xlabel("Risk Ratio (RR) associated with\nunmeasured confounder", fontsize=11)
ax.set_ylabel("Required E-value\n(minimum RR for both paths)", fontsize=11)
ax.set_title(
    "E-value Analysis: Required Unmeasured Confounding\nto Explain Away the Observed Association",
    fontsize=11, fontweight="bold"
)
ax.legend(fontsize=9, loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
out_path = os.path.join(FIGURES_DIR, "evalue_visualization.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()
logger.info(f"Figure 8 保存: {out_path}")

logger.info("Phase 4b 完了: 追加図3枚生成")
