"""
Phase 3: 統計解析（修正版）
歯周病率（K05/10万人）と糖尿病指標の関連を OLS 回帰で検定する。
感度分析7仕様で頑健性を確認（Spec7: 所得調整追加）。
陰性対照（う蝕率）解析を追加。Moran's Iで空間的自己相関を確認。

入力: 02_Data/interim/analysis_dataset.csv（income_per_capita 列含む）
出力:
  - 03_Analysis/results/regression_results.csv
  - 03_Analysis/results/sensitivity_analysis_results.csv
  - 03_Analysis/results/negative_control_results.csv
  - 03_Analysis/results/morans_i_results.txt
"""
import os
import sys
import pandas as pd
import numpy as np
import yaml
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

PROJECT_ROOT = "C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub"
PROJECT_DIR = os.path.join(PROJECT_ROOT, "projects", "NDB_XXX_dental_systemic")
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from ndb_library.logger import setup_logger

logger = setup_logger(__name__, log_file=os.path.join(PROJECT_DIR, "03_Analysis", "analysis", "logs", "phase3_regression.log"))

with open(os.path.join(PROJECT_DIR, "config", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

INTERIM_DIR = os.path.join(PROJECT_DIR, config["output"]["interim_dir"])
RESULTS_DIR = os.path.join(PROJECT_DIR, config["output"]["results_dir"])
os.makedirs(RESULTS_DIR, exist_ok=True)

# ========================================
# データ読み込み
# ========================================
data_path = os.path.join(INTERIM_DIR, config["output"]["files"]["analysis_dataset"])
df = pd.read_csv(data_path, encoding="utf-8")
logger.info(f"解析データ読み込み: {len(df)}行")
logger.info(f"カラム: {df.columns.tolist()}")

# アウトカム変数リスト
OUTCOMES = ["hba1c_high_rate", "hba1c_mean", "dm_complication_rate", "dialysis_prevention_rate"]
OUTCOMES = [o for o in OUTCOMES if o in df.columns]
EXPOSURE = "periodontal_rate"
COVARIATES = ["aging_rate", "pop_density"]

# 共変量の存在確認
COVARIATES = [c for c in COVARIATES if c in df.columns]
logger.info(f"アウトカム変数: {OUTCOMES}")
logger.info(f"曝露変数: {EXPOSURE}")
logger.info(f"調整変数: {COVARIATES}")

# ========================================
# 関数定義
# ========================================
def run_ols(df_sub, outcome, exposure, covariates, robust=None):
    """OLS回帰を実行し、主要な統計量を返す"""
    y = df_sub[outcome].dropna()
    X_cols = [exposure] + covariates
    X = df_sub.loc[y.index, X_cols].dropna()
    y = y.loc[X.index]

    X_const = sm.add_constant(X)
    # HC3 ロバスト SE は fit(cov_type=) で指定
    if robust:
        model = sm.OLS(y, X_const).fit(cov_type=robust)
    else:
        model = sm.OLS(y, X_const).fit()

    n = len(y)
    beta = float(model.params[exposure])
    se = float(model.bse[exposure])
    pval = float(model.pvalues[exposure])
    ci = model.conf_int()  # columns: 0 (lower), 1 (upper)
    ci_lo = float(ci.loc[exposure, 0])
    ci_hi = float(ci.loc[exposure, 1])
    r2 = model.rsquared

    return {
        "n": n,
        "beta": beta,
        "se": se,
        "p_value": pval,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "r2": r2,
    }

def calc_vif(df_sub, exposure, covariates):
    """VIFを計算して多重共線性を確認"""
    X = df_sub[[exposure] + covariates].dropna()
    X_const = sm.add_constant(X)
    vif_data = {col: variance_inflation_factor(X_const.values, i)
                for i, col in enumerate(X_const.columns)}
    return vif_data

# ========================================
# VIF チェック（多重共線性）
# ========================================
logger.info("VIF（多重共線性）チェック:")
vif = calc_vif(df, EXPOSURE, COVARIATES)
for var, v in vif.items():
    logger.info(f"  {var}: VIF={v:.2f}")
    if v > 5.0:
        logger.warning(f"  → VIF > 5.0: {var} に多重共線性の疑い")

# ========================================
# 感度分析 7 仕様（Spec7: 所得追加調整）
# ========================================
specs = config["analysis"]["sensitivity_analyses"]

# Spec7: 所得調整（income_per_capitaが存在する場合のみ有効）
spec7 = {
    "name": "Spec7_IncomeAdjusted",
    "description": "所得（income_per_capita）追加調整",
    "covariates": ["aging_rate", "pop_density", "income_per_capita"],
}
if "income_per_capita" in df.columns:
    specs = list(specs) + [spec7]
    logger.info("Spec7（所得調整）を感度分析に追加しました")
else:
    logger.warning("income_per_capita 列が存在しないため Spec7 をスキップします")

METRO_PREFS = ["東京都", "大阪府", "愛知県"]

all_results = []

for outcome in OUTCOMES:
    logger.info(f"\n{'='*40}")
    logger.info(f"アウトカム: {outcome}")

    for spec in specs:
        spec_name = spec["name"]
        covariates = spec.get("covariates", COVARIATES)
        covariates = [c for c in covariates if c in df.columns]
        robust = spec.get("robust", None)

        df_sub = df.copy()

        # 外れ値除外
        if spec.get("outlier_exclusion"):
            for col in [EXPOSURE, outcome]:
                if col in df_sub.columns:
                    m, s = df_sub[col].mean(), df_sub[col].std()
                    df_sub = df_sub[(df_sub[col] - m).abs() <= 3 * s]

        # 大都市圏除外
        if spec.get("exclude_prefectures"):
            excl = spec["exclude_prefectures"]
            df_sub = df_sub[~df_sub["prefecture"].isin(excl)]

        # 対数変換
        if spec.get("log_transform"):
            df_sub = df_sub.copy()
            for col in [EXPOSURE, outcome]:
                if col in df_sub.columns:
                    df_sub[col] = np.log1p(df_sub[col])

        try:
            res = run_ols(df_sub, outcome, EXPOSURE, covariates, robust=robust)
            res.update({
                "outcome": outcome,
                "specification": spec_name,
                "significant": res["p_value"] < 0.05,
            })
            all_results.append(res)
            sig_mark = "*" if res["significant"] else ""
            logger.info(
                f"  [{spec_name}] beta={res['beta']:.4f}, p={res['p_value']:.3f}{sig_mark}, "
                f"R2={res['r2']:.3f}, n={res['n']}"
            )
        except Exception as e:
            logger.error(f"  [{spec_name}] エラー: {e}")

# ========================================
# 頑健性サマリー
# ========================================
df_res = pd.DataFrame(all_results)
logger.info("\n===== 頑健性サマリー =====")
for outcome in OUTCOMES:
    sub = df_res[df_res["outcome"] == outcome]
    n_sig = sub["significant"].sum()
    n_total = len(sub)
    logger.info(f"{outcome}: {n_sig}/{n_total} 仕様で有意 (p<0.05)")

# ========================================
# 主解析結果（Spec1_Baseline）
# ========================================
df_baseline = df_res[df_res["specification"] == "Spec1_Baseline"].copy()
df_baseline["outcome_label"] = df_baseline["outcome"]
df_baseline.to_csv(os.path.join(RESULTS_DIR, config["output"]["files"]["regression_results"]),
                   index=False, encoding="utf-8")
logger.info(f"\n主解析結果を保存: {config['output']['files']['regression_results']}")

# 全感度分析結果
df_res.to_csv(os.path.join(RESULTS_DIR, config["output"]["files"]["sensitivity_results"]),
              index=False, encoding="utf-8")
logger.info(f"感度分析結果を保存: {config['output']['files']['sensitivity_results']}")

# ========================================
# 陰性対照解析（Negative Control: caries_rate）
# ========================================
# う蝕率（caries_rate）は歯科疾患だが全身性炎症との直接経路がない。
# periodontal_rateと同様の社会経済的決定要因を共有しつつも、
# 生物学的経路（炎症→インスリン抵抗性）を持たないため陰性対照として適切。
if "caries_rate" in df.columns:
    logger.info("\n===== 陰性対照解析（caries_rate） =====")
    NEGATIVE_CONTROL = "caries_rate"
    # 主要アウトカム（dm_complication_rate）と全アウトカムに対して解析
    nc_specs_names = ["Spec1_Baseline", "Spec2_HC3", "Spec3_OutlierExcluded",
                      "Spec4_MetropolisExcluded", "Spec5_LogTransformed", "Spec6_AgingOnly"]
    nc_specs_to_run = [s for s in specs if s["name"] in nc_specs_names]

    nc_results = []
    for outcome in OUTCOMES:
        for spec in nc_specs_to_run:
            spec_name = spec["name"]
            covariates = spec.get("covariates", COVARIATES)
            covariates = [c for c in covariates if c in df.columns]
            robust = spec.get("robust", None)

            df_sub = df.copy()
            if spec.get("outlier_exclusion"):
                for col in [NEGATIVE_CONTROL, outcome]:
                    if col in df_sub.columns:
                        m, s = df_sub[col].mean(), df_sub[col].std()
                        df_sub = df_sub[(df_sub[col] - m).abs() <= 3 * s]
            if spec.get("exclude_prefectures"):
                df_sub = df_sub[~df_sub["prefecture"].isin(spec["exclude_prefectures"])]
            if spec.get("log_transform"):
                for col in [NEGATIVE_CONTROL, outcome]:
                    if col in df_sub.columns:
                        df_sub[col] = np.log1p(df_sub[col])

            try:
                res = run_ols(df_sub, outcome, NEGATIVE_CONTROL, covariates, robust=robust)
                res.update({
                    "exposure": NEGATIVE_CONTROL,
                    "outcome": outcome,
                    "specification": spec_name,
                    "significant": res["p_value"] < 0.05,
                })
                nc_results.append(res)
                sig_mark = "* [CAUTION: confounding possible]" if res["significant"] else ""
                logger.info(
                    f"  [{outcome} | {spec_name}] beta={res['beta']:.4f}, "
                    f"p={res['p_value']:.3f}{sig_mark}"
                )
            except Exception as e:
                logger.error(f"  [{outcome} | {spec_name}] エラー: {e}")

    # 陰性対照サマリー
    df_nc = pd.DataFrame(nc_results)
    logger.info("\n----- 陰性対照（う蝕率）頑健性サマリー -----")
    for outcome in OUTCOMES:
        sub = df_nc[df_nc["outcome"] == outcome]
        n_sig = sub["significant"].sum()
        n_total = len(sub)
        if n_sig == 0:
            logger.info(f"{outcome}: {n_sig}/{n_total} → 特異性支持（社会経済的confoundingの懸念 小）")
        else:
            logger.warning(f"{outcome}: {n_sig}/{n_total} → 非特異的関連の可能性（confounding 要考慮）")

    df_nc.to_csv(os.path.join(RESULTS_DIR, "negative_control_results.csv"),
                 index=False, encoding="utf-8")
    logger.info("陰性対照解析結果を保存: negative_control_results.csv")
else:
    logger.warning("caries_rate 列が存在しないため陰性対照解析をスキップします")

# ========================================
# Moran's I（空間的自己相関）
# ========================================
try:
    import geopandas as gpd
    from libpysal.weights import Queen
    from esda.moran import Moran

    GIS_PATH = os.path.join(PROJECT_ROOT, "02_Data", "raw", "GIS", "japan.geojson")
    gdf = gpd.read_file(GIS_PATH)
    gdf["pref_code"] = gdf["id"].astype(str).str.zfill(2)

    # 都道府県コードと都道府県名のマッピング
    pref_code_map = {
        "01": "北海道", "02": "青森県", "03": "岩手県", "04": "宮城県", "05": "秋田県",
        "06": "山形県", "07": "福島県", "08": "茨城県", "09": "栃木県", "10": "群馬県",
        "11": "埼玉県", "12": "千葉県", "13": "東京都", "14": "神奈川県", "15": "新潟県",
        "16": "富山県", "17": "石川県", "18": "福井県", "19": "山梨県", "20": "長野県",
        "21": "岐阜県", "22": "静岡県", "23": "愛知県", "24": "三重県", "25": "滋賀県",
        "26": "京都府", "27": "大阪府", "28": "兵庫県", "29": "奈良県", "30": "和歌山県",
        "31": "鳥取県", "32": "島根県", "33": "岡山県", "34": "広島県", "35": "山口県",
        "36": "徳島県", "37": "香川県", "38": "愛媛県", "39": "高知県", "40": "福岡県",
        "41": "佐賀県", "42": "長崎県", "43": "熊本県", "44": "大分県", "45": "宮崎県",
        "46": "鹿児島県", "47": "沖縄県"
    }
    gdf["prefecture"] = gdf["pref_code"].map(pref_code_map)
    gdf_merged = gdf.merge(df[["prefecture", EXPOSURE]], on="prefecture", how="inner")

    w = Queen.from_dataframe(gdf_merged, silence_warnings=True)
    w.transform = "r"
    y_moran = gdf_merged[EXPOSURE].values
    moran = Moran(y_moran, w)

    moran_txt = (
        f"Moran's I for {EXPOSURE}:\n"
        f"  I = {moran.I:.4f}\n"
        f"  p-value (sim) = {moran.p_sim:.4f}\n"
        f"  z-score = {moran.z_sim:.4f}\n"
        f"  解釈: {'有意な空間的自己相関あり' if moran.p_sim < 0.05 else '有意な空間的自己相関なし'}\n"
    )
    logger.info(moran_txt)

    with open(os.path.join(RESULTS_DIR, "morans_i_results.txt"), "w", encoding="utf-8") as f:
        f.write(moran_txt)

    # ========================================
    # Spec8: 空間回帰モデル（SEM/SLM）
    # Moran's I が有意なため OLS 残差の独立性が保証されない。
    # LM テストで SEM/SLM を選択し、感度分析 Spec8 として追記する。
    # ========================================
    try:
        import spreg
        from spreg import ML_Error, ML_Lag

        spec8_results = []

        for outcome in OUTCOMES:
            try:
                # データ整備（NaN 除去）
                cols_needed = ["prefecture", EXPOSURE] + COVARIATES + [outcome]
                df_sp = df[[c for c in cols_needed if c in df.columns]].dropna()
                gdf_sp = gdf.merge(df_sp, on="prefecture", how="inner")

                if len(gdf_sp) < 20:
                    logger.warning(f"Spec8 [{outcome}]: マッチ都道府県数が少なすぎます ({len(gdf_sp)}) → スキップ")
                    continue

                w_sp = Queen.from_dataframe(gdf_sp, silence_warnings=True)
                w_sp.transform = "r"

                y_sp = gdf_sp[outcome].values.reshape(-1, 1)
                x_names_sp = [EXPOSURE] + [c for c in COVARIATES if c in gdf_sp.columns]
                X_sp = gdf_sp[x_names_sp].values

                # LM テスト（spreg.OLS で空間診断付き）
                ols_sp = spreg.OLS(
                    y_sp, X_sp, w=w_sp,
                    name_y=outcome, name_x=x_names_sp,
                    spat_diag=True
                )

                lm_lag_p    = ols_sp.lm_lag[1]    if ols_sp.lm_lag    else 1.0
                lm_error_p  = ols_sp.lm_error[1]  if ols_sp.lm_error  else 1.0
                rlm_lag_p   = ols_sp.rlm_lag[1]   if ols_sp.rlm_lag   else 1.0
                rlm_error_p = ols_sp.rlm_error[1] if ols_sp.rlm_error else 1.0

                logger.info(
                    f"Spec8 LM tests [{outcome}]: "
                    f"LM-Lag p={lm_lag_p:.3f}, LM-Error p={lm_error_p:.3f}, "
                    f"RLM-Lag p={rlm_lag_p:.3f}, RLM-Error p={rlm_error_p:.3f}"
                )

                # Anselin (1988) の決定ルール
                # LM テスト非有意 → OLS が適切、Spec8 不要
                if lm_lag_p >= 0.05 and lm_error_p >= 0.05:
                    logger.info(
                        f"  Spec8 [{outcome}]: LM テスト非有意 → OLS が適切（空間回帰不要）"
                    )
                    spec8_results.append({
                        "outcome": outcome,
                        "specification": "Spec8_LM_ns_OLS_OK",
                        "n": len(gdf_sp),
                        "beta": float("nan"),
                        "se": float("nan"),
                        "p_value": float("nan"),
                        "ci_lower": float("nan"),
                        "ci_upper": float("nan"),
                        "r2": float("nan"),
                        "significant": False,
                    })
                    continue

                if rlm_lag_p < rlm_error_p:
                    model_sp = ML_Lag(y_sp, X_sp, w=w_sp, name_y=outcome, name_x=x_names_sp)
                    model_type = "SLM"
                else:
                    model_sp = ML_Error(y_sp, X_sp, w=w_sp, name_y=outcome, name_x=x_names_sp)
                    model_type = "SEM"

                # 曝露変数の係数抽出（vm を使った頑健な方法）
                # z_stat は最適化失敗時に 0 次元配列になる場合があるため vm から計算
                from scipy.stats import norm as _norm
                beta_sp = float(np.squeeze(model_sp.betas[1]))
                se_sp = float(np.sqrt(np.squeeze(model_sp.vm[1, 1])))
                if se_sp > 0 and not np.isnan(se_sp):
                    z_val = beta_sp / se_sp
                    p_sp  = float(2 * (1 - _norm.cdf(abs(z_val))))
                else:
                    z_val = float("nan")
                    p_sp  = float("nan")
                ci_lo_sp = beta_sp - 1.96 * se_sp
                ci_hi_sp = beta_sp + 1.96 * se_sp
                pr2_sp = float(model_sp.pr2) if hasattr(model_sp, "pr2") else float("nan")

                spec8_results.append({
                    "outcome": outcome,
                    "specification": f"Spec8_{model_type}",
                    "n": len(gdf_sp),
                    "beta": beta_sp,
                    "se": se_sp,
                    "p_value": p_sp,
                    "ci_lower": ci_lo_sp,
                    "ci_upper": ci_hi_sp,
                    "r2": pr2_sp,
                    "significant": p_sp < 0.05,
                })

                sig_mark = "*" if p_sp < 0.05 else ""
                logger.info(
                    f"  Spec8 [{outcome}] {model_type}: beta={beta_sp:.4f}, "
                    f"p={p_sp:.3f}{sig_mark}, n={len(gdf_sp)}"
                )

            except Exception as e_outcome:
                logger.error(f"Spec8 [{outcome}] エラー: {e_outcome}")

        # 感度分析 CSV に Spec8 を追記
        if spec8_results:
            df_spec8 = pd.DataFrame(spec8_results)
            df_res_upd = pd.concat([df_res, df_spec8], ignore_index=True)
            df_res_upd.to_csv(
                os.path.join(RESULTS_DIR, config["output"]["files"]["sensitivity_results"]),
                index=False, encoding="utf-8"
            )
            logger.info("Spec8（空間回帰）を sensitivity_analysis_results.csv に追記しました")

            # 空間回帰の詳細テキストを保存
            spatial_txt_path = os.path.join(RESULTS_DIR, "spatial_regression_spec8.txt")
            with open(spatial_txt_path, "w", encoding="utf-8") as f:
                f.write("空間回帰モデル（Spec8）詳細結果\n")
                f.write("=" * 50 + "\n")
                for r in spec8_results:
                    f.write(f"\nアウトカム: {r['outcome']}  モデル: {r['specification']}\n")
                    f.write(f"  β={r['beta']:.5f}, SE={r['se']:.5f}, p={r['p_value']:.4f}\n")
                    f.write(f"  95%CI=[{r['ci_lower']:.5f}, {r['ci_upper']:.5f}]\n")
                    f.write(f"  Pseudo-R²={r['r2']:.3f}, n={r['n']}\n")
                    f.write(f"  有意(p<0.05): {'Yes *' if r['significant'] else 'No'}\n")
            logger.info(f"空間回帰詳細を保存: {spatial_txt_path}")

    except ImportError as e_spreg:
        logger.warning(f"spreg がインストールされていないため Spec8 をスキップします: {e_spreg}")
    except Exception as e_sp:
        logger.error(f"Spec8（空間回帰）エラー: {e_sp}")

except ImportError:
    logger.warning("libpysal/esda がインストールされていないため Moran's I をスキップします")
except Exception as e:
    logger.error(f"Moran's I 計算エラー: {e}")

logger.info("Phase 3 完了")
