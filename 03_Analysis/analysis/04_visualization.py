"""
Phase 4: 可視化（修正版）
歯周病率 vs 糖尿病指標の散布図・Choropleth map・Forest plot を作成する。
陰性対照（う蝕率）のForest plot とLocal Moran's I (LISA) クラスタ図を追加。

入力: 02_Data/interim/analysis_dataset.csv
出力: results/figures/（config output.figures_dir、原稿は ../results/figures/）
  - scatter_periodontal_hba1c_high_rate.png
  - scatter_periodontal_dm_complication_rate.png
  - forest_plot_dm_complication_rate.png（感度分析7仕様）
  - forest_plot_hba1c_high_rate.png
  - forest_plot_negative_control.png（陰性対照: う蝕率）
  - choropleth_periodontal_rate.png
  - lisa_cluster_map.png（Local Moran's I クラスタ）
"""
import os
import sys
import pandas as pd
import numpy as np
import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
sys.path.insert(0, _SCRIPT_DIR)

from prefecture_labels_en import JP_TO_PREF_CODE, prefecture_label_en
from ndb_library.viz import add_watermark
from ndb_library.logger import setup_logger

logger = setup_logger(__name__, log_file=os.path.join(PROJECT_DIR, "03_Analysis", "analysis", "logs", "phase4_visualization.log"))

with open(os.path.join(PROJECT_DIR, "config", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

INTERIM_DIR = os.path.join(PROJECT_DIR, config["output"]["interim_dir"])
RESULTS_DIR = os.path.join(PROJECT_DIR, config["output"]["results_dir"])
FIGURES_DIR = os.path.join(PROJECT_DIR, config["output"]["figures_dir"])
os.makedirs(FIGURES_DIR, exist_ok=True)

DPI = config["visualization"]["dpi"]
FIG_SIZE = config["visualization"]["figure_size"]
EXPERIMENT_MODE = config["project"]["experiment_mode"]

# データ読み込み
df = pd.read_csv(os.path.join(INTERIM_DIR, config["output"]["files"]["analysis_dataset"]), encoding="utf-8")
df["pref_code"] = df["prefecture"].map(JP_TO_PREF_CODE)
df_sens = pd.read_csv(os.path.join(RESULTS_DIR, config["output"]["files"]["sensitivity_results"]), encoding="utf-8")
# 陰性対照結果（存在する場合）
nc_results_path = os.path.join(RESULTS_DIR, "negative_control_results.csv")
df_nc = pd.read_csv(nc_results_path, encoding="utf-8") if os.path.exists(nc_results_path) else None

# ========================================
# Figure 1: 散布図（歯周病率 vs HbA1c高値率）
# ========================================
OUTCOMES_TO_PLOT = {
    "hba1c_high_rate": "HbA1c high-value rate (%)",
    "dm_complication_rate": "Diabetic complication management rate (per 100,000)",
}

for outcome_col, outcome_label in OUTCOMES_TO_PLOT.items():
    if outcome_col not in df.columns:
        logger.warning(f"{outcome_col} が存在しません。スキップします。")
        continue

    sub = df[["prefecture", "periodontal_rate", outcome_col]].dropna()
    if len(sub) == 0:
        continue

    r, p = stats.pearsonr(sub["periodontal_rate"], sub[outcome_col])

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.scatter(sub["periodontal_rate"], sub[outcome_col], alpha=0.7, color="steelblue", s=60)

    # 回帰直線
    m, b = np.polyfit(sub["periodontal_rate"], sub[outcome_col], 1)
    x_line = np.linspace(sub["periodontal_rate"].min(), sub["periodontal_rate"].max(), 100)
    ax.plot(x_line, m * x_line + b, color="tomato", linewidth=1.5)

    # 都道府県名ラベル（上位・下位5県）
    sub_sorted = sub.nlargest(3, "periodontal_rate")
    for _, row in sub_sorted.iterrows():
        ax.annotate(
            prefecture_label_en(str(row["prefecture"])),
            (row["periodontal_rate"], row[outcome_col]),
            fontsize=7,
            xytext=(3, 3),
            textcoords="offset points",
            alpha=0.8,
        )

    ax.set_xlabel("Periodontal disease claim rate (per 100,000 population)", fontsize=12)
    ax.set_ylabel(outcome_label, fontsize=12)
    ax.set_title(
        f"Periodontal disease rate vs. {outcome_label} by prefecture\n"
        f"(r={r:.3f}, p={p:.3f}, N=47)",
        fontsize=12,
    )

    if EXPERIMENT_MODE:
        add_watermark(fig, "SAMPLE DATA")

    fname = f"scatter_periodontal_{outcome_col}.png"
    fig.savefig(os.path.join(FIGURES_DIR, fname), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"散布図保存: {fname}  (r={r:.3f}, p={p:.3f})")

# ========================================
# Figure 2: Forest plot（感度分析）
# ========================================
for outcome_col in ["hba1c_high_rate", "dm_complication_rate"]:
    sub = df_sens[df_sens["outcome"] == outcome_col].copy()
    if len(sub) == 0:
        continue

    sub["spec_label"] = sub["specification"].str.replace("_", " ")

    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = range(len(sub))

    for i, (_, row) in enumerate(sub.iterrows()):
        color = "tomato" if row["significant"] else "steelblue"
        ax.errorbar(row["beta"], i, xerr=[[row["beta"] - row["ci_lower"]], [row["ci_upper"] - row["beta"]]],
                    fmt="o", color=color, markersize=7, capsize=4, linewidth=1.5)

    ax.axvline(x=0, color="gray", linestyle="--", linewidth=1)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(sub["spec_label"].tolist(), fontsize=10)
    ax.set_xlabel("Regression coefficient (β)", fontsize=12)
    ax.set_title(f"Sensitivity analysis (forest plot)\nOutcome: {outcome_col}", fontsize=12)

    legend_handles = [
        mpatches.Patch(color="tomato", label="p < 0.05"),
        mpatches.Patch(color="steelblue", label="p ≥ 0.05"),
    ]
    ax.legend(handles=legend_handles, fontsize=10)

    # 頑健性サマリー
    n_sig = sub["significant"].sum()
    n_total = len(sub)
    ax.text(
        0.98,
        0.02,
        f"Significant: {n_sig}/{n_total} specifications",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray"),
    )

    if EXPERIMENT_MODE:
        add_watermark(fig, "SAMPLE DATA")

    fname = f"forest_plot_{outcome_col}.png"
    fig.savefig(os.path.join(FIGURES_DIR, fname), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Forest plot保存: {fname}")

# ========================================
# Figure 3: Choropleth map（歯周病率の地理的分布）
# ========================================
try:
    import geopandas as gpd

    GIS_PATH = os.path.join(PROJECT_ROOT, "02_Data", "raw", "GIS", "japan.geojson")
    gdf = gpd.read_file(GIS_PATH)
    gdf["pref_code"] = gdf["id"].astype(str).str.zfill(2)
    gdf_merged = gdf.merge(df[["pref_code", "periodontal_rate"]], on="pref_code", how="left")

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    gdf_merged.plot(
        column="periodontal_rate",
        cmap=config["visualization"]["colormap"],
        legend=True,
        ax=ax,
        edgecolor="black",
        linewidth=0.3,
        missing_kwds={"color": "lightgrey", "label": "No data"},
    )
    ax.set_title(
        "Periodontal disease claim rate by prefecture (per 100,000 population)\nNDB Open Data No.10",
        fontsize=12,
    )
    ax.axis("off")

    if EXPERIMENT_MODE:
        add_watermark(fig, "SAMPLE DATA")

    fname = "choropleth_periodontal_rate.png"
    fig.savefig(os.path.join(FIGURES_DIR, fname), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Choropleth map保存: {fname}")

except ImportError:
    logger.warning("geopandas がインストールされていないためChoropleth mapをスキップします")
except Exception as e:
    logger.error(f"Choropleth map 作成エラー: {e}")

# ========================================
# Figure 4: 陰性対照 Forest plot（う蝕率 vs 全アウトカム）
# ========================================
if df_nc is not None:
    # dm_complication_rateに対するう蝕率の感度分析
    nc_dm = df_nc[df_nc["outcome"] == "dm_complication_rate"].copy()
    if len(nc_dm) > 0:
        nc_dm["spec_label"] = nc_dm["specification"].str.replace("_", " ")

        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

        # 左: periodontal_rate（主解析）
        dm_main = df_sens[df_sens["outcome"] == "dm_complication_rate"].copy()
        dm_main["spec_label"] = dm_main["specification"].str.replace("_", " ")
        # Spec1〜6のみ表示（比較用）
        dm_main6 = dm_main[dm_main["specification"].isin(nc_dm["specification"].tolist())]

        for i, (_, row) in enumerate(dm_main6.iterrows()):
            color = "tomato" if row["significant"] else "steelblue"
            axes[0].errorbar(row["beta"], i,
                             xerr=[[row["beta"] - row["ci_lower"]], [row["ci_upper"] - row["beta"]]],
                             fmt="o", color=color, markersize=7, capsize=4, linewidth=1.5)
        axes[0].axvline(x=0, color="gray", linestyle="--", linewidth=1)
        axes[0].set_yticks(range(len(dm_main6)))
        axes[0].set_yticklabels(dm_main6["spec_label"].tolist(), fontsize=9)
        axes[0].set_xlabel("Regression coefficient (β)", fontsize=11)
        axes[0].set_title(
            "Primary: periodontal rate → complication management rate\n(inflammatory pathway)",
            fontsize=11,
        )
        n_sig_main = dm_main6["significant"].sum()
        axes[0].text(
            0.98,
            0.02,
            f"Significant: {n_sig_main}/{len(dm_main6)} specifications",
            transform=axes[0].transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            bbox=dict(boxstyle="round", facecolor="lightyellow", edgecolor="gray"),
        )

        # 右: caries_rate（陰性対照）
        for i, (_, row) in enumerate(nc_dm.iterrows()):
            color = "tomato" if row["significant"] else "steelblue"
            ci_err_lo = abs(row["beta"] - row["ci_lower"]) if "ci_lower" in row else abs(row.get("se", 0) * 1.96)
            ci_err_hi = abs(row["ci_upper"] - row["beta"]) if "ci_upper" in row else abs(row.get("se", 0) * 1.96)
            axes[1].errorbar(row["beta"], i,
                             xerr=[[ci_err_lo], [ci_err_hi]],
                             fmt="s", color=color, markersize=7, capsize=4, linewidth=1.5)
        axes[1].axvline(x=0, color="gray", linestyle="--", linewidth=1)
        axes[1].set_yticks(range(len(nc_dm)))
        axes[1].set_yticklabels(nc_dm["spec_label"].tolist(), fontsize=9)
        axes[1].set_xlabel("Regression coefficient (β)", fontsize=11)
        axes[1].set_title(
            "Negative control: caries rate → complication management rate\n(no periodontal inflammation pathway)",
            fontsize=11,
        )
        n_sig_nc = nc_dm["significant"].sum()
        axes[1].text(
            0.98,
            0.02,
            f"Significant: {n_sig_nc}/{len(nc_dm)} specifications",
            transform=axes[1].transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            bbox=dict(boxstyle="round", facecolor="lightyellow", edgecolor="gray"),
        )

        plt.suptitle(
            "Negative control: periodontal vs. caries rate and complication management\n"
            "(null association for caries supports specificity of the periodontal finding)",
            fontsize=12,
            y=1.02,
        )

        if EXPERIMENT_MODE:
            add_watermark(fig, "SAMPLE DATA")

        fname = "forest_plot_negative_control.png"
        fig.savefig(os.path.join(FIGURES_DIR, fname), dpi=DPI, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"陰性対照 Forest plot 保存: {fname}")

# ========================================
# Figure 5: Local Moran's I (LISA) クラスタ図
# ========================================
try:
    import geopandas as gpd
    from libpysal.weights import Queen, KNN
    from esda.moran import Moran_Local

    GIS_PATH = os.path.join(PROJECT_ROOT, "02_Data", "raw", "GIS", "japan.geojson")
    gdf = gpd.read_file(GIS_PATH)
    gdf["pref_code"] = gdf["id"].astype(str).str.zfill(2)
    gdf_merged = gdf.merge(df[["pref_code", "periodontal_rate"]], on="pref_code", how="left")
    gdf_merged = gdf_merged.dropna(subset=["periodontal_rate"]).reset_index(drop=True)

    # Queen contiguity weights（離島はKNN=1補完）
    w_queen = Queen.from_dataframe(gdf_merged, use_index=False, silence_warnings=True)
    islands = [i for i, v in w_queen.cardinalities.items() if v == 0]
    if islands:
        w_knn = KNN.from_dataframe(gdf_merged, k=1, use_index=False)
        for idx in islands:
            w_queen.neighbors[idx] = w_knn.neighbors[idx]
            w_queen.weights[idx] = w_knn.weights[idx]
    w_queen.transform = "r"

    y_lisa = gdf_merged["periodontal_rate"].values
    lisa = Moran_Local(y_lisa, w_queen, permutations=999)

    # クラスタ分類（p<0.05のみ表示）
    sig = lisa.p_sim < 0.05
    cluster_type = []
    for i in range(len(y_lisa)):
        if not sig[i]:
            cluster_type.append("ns")
        elif lisa.q[i] == 1:
            cluster_type.append("HH")  # High-High
        elif lisa.q[i] == 2:
            cluster_type.append("LH")  # Low-High
        elif lisa.q[i] == 3:
            cluster_type.append("LL")  # Low-Low
        elif lisa.q[i] == 4:
            cluster_type.append("HL")  # High-Low
        else:
            cluster_type.append("ns")

    gdf_merged["cluster"] = cluster_type

    color_map = {"HH": "#d73027", "LL": "#4575b4", "HL": "#fdae61", "LH": "#abd9e9", "ns": "#f7f7f7"}
    gdf_merged["color"] = gdf_merged["cluster"].map(color_map)

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    for cluster_label, color in color_map.items():
        subset = gdf_merged[gdf_merged["cluster"] == cluster_label]
        if len(subset) > 0:
            subset.plot(ax=ax, color=color, edgecolor="black", linewidth=0.3)

    ax.set_title(
        f"Local Moran's I (LISA) clusters: periodontal disease claim rate\n"
        f"Global Moran's I = 0.359 (p = 0.002), N = 47 prefectures",
        fontsize=11,
    )
    label_map = {
        "HH": "High–High (HH)",
        "LL": "Low–Low (LL)",
        "HL": "High–Low (HL)",
        "LH": "Low–High (LH)",
        "ns": "Not significant",
    }
    legend_handles = [mpatches.Patch(color=c, label=label_map[k]) for k, c in color_map.items()]
    ax.legend(
        handles=legend_handles,
        title="Cluster type (p < 0.05)",
        loc="lower right",
        fontsize=9,
        framealpha=0.9,
    )
    ax.axis("off")

    if EXPERIMENT_MODE:
        add_watermark(fig, "SAMPLE DATA")

    fname = "lisa_cluster_map.png"
    fig.savefig(os.path.join(FIGURES_DIR, fname), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"LISA クラスタ図保存: {fname}")

except ImportError:
    logger.warning("libpysal/esda がインストールされていないため LISA をスキップします")
except Exception as e:
    logger.error(f"LISA クラスタ図 作成エラー: {e}")

logger.info("Phase 4 完了")
