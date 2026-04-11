"""
Phase 2: データ統合
歯科傷病データ（Phase 1出力）と既存HbA1cプロジェクトのアウトカム変数を統合し、
解析用データセットを作成する。

入力:
  - 02_Data/interim/dental_disease_prefecture.csv（Phase 1出力）
  - projects/NDB_XXX_hba1c_complications/data/interim/analysis_dataset_phase1.csv（既存）

出力: 02_Data/interim/analysis_dataset.csv
"""
import os
import sys
import pandas as pd
import yaml

PROJECT_ROOT = "C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub"
PROJECT_DIR = os.path.join(PROJECT_ROOT, "projects", "NDB_XXX_dental_systemic")
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from ndb_library.logger import setup_logger

logger = setup_logger(__name__, log_file=os.path.join(PROJECT_DIR, "03_Analysis", "analysis", "logs", "phase2_integrate.log"))

with open(os.path.join(PROJECT_DIR, "config", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

INTERIM_DIR = os.path.join(PROJECT_DIR, config["output"]["interim_dir"])

# ========================================
# Step 1: 歯科傷病データ読み込み（Phase 1出力）
# ========================================
dental_path = os.path.join(INTERIM_DIR, config["output"]["files"]["dental_data"])
logger.info(f"歯科傷病データ読み込み: {dental_path}")
df_dental = pd.read_csv(dental_path, encoding="utf-8")
logger.info(f"歯科傷病データ: {len(df_dental)}行, カラム: {df_dental.columns.tolist()}")

# ========================================
# Step 2: 既存HbA1cデータ読み込み
# ========================================
hba1c_path = config["data_sources"]["hba1c_existing"]["path"]
logger.info(f"既存HbA1cデータ読み込み: {hba1c_path}")
df_hba1c = pd.read_csv(hba1c_path, encoding="utf-8")
logger.info(f"既存HbA1cデータ: {len(df_hba1c)}行, カラム: {df_hba1c.columns.tolist()}")

# ========================================
# Step 3: 変数選択（既存データから必要なカラムのみ）
# ========================================
outcome_cols = ["prefecture",
                "hba1c_high_rate", "hba1c_mean",
                "dm_complication_rate", "dialysis_prevention_rate",
                "aging_rate", "pop_density"]

# 実際のカラム名を確認しながら選択（存在しない列は警告）
available_cols = [c for c in outcome_cols if c in df_hba1c.columns]
missing_cols = [c for c in outcome_cols if c not in df_hba1c.columns]
if missing_cols:
    logger.warning(f"既存データに存在しない列: {missing_cols}")
    logger.info(f"利用可能な列: {df_hba1c.columns.tolist()}")

df_outcomes = df_hba1c[available_cols].copy()

# ========================================
# Step 4: 社会経済データ（所得）読み込み
# ========================================
UNEMPLOYMENT_PROJECT = os.path.join(PROJECT_ROOT, "projects", "NDB_XXX_diabetes_unemployment")
income_path = os.path.join(UNEMPLOYMENT_PROJECT, "data", "interim", "analysis_dataset_with_unemployment.csv")
logger.info(f"所得データ読み込み: {income_path}")
df_income = pd.read_csv(income_path, encoding="utf-8-sig")
df_income = df_income[["prefecture", "income_per_capita"]].copy()
logger.info(f"所得データ: {len(df_income)}行")

# ========================================
# Step 5: 歯科傷病データとアウトカムデータの結合
# ========================================
df_analysis = pd.merge(
    df_dental[["prefecture", "periodontal_rate", "chronic_periodontal_rate", "caries_rate",
               "periodontal_count", "chronic_periodontal_count", "caries_count"]],
    df_outcomes,
    on="prefecture",
    how="inner"
)
# 所得データを追加
df_analysis = pd.merge(df_analysis, df_income, on="prefecture", how="left")
logger.info(f"統合後データ: {len(df_analysis)}行（47であれば正常）")

if len(df_analysis) != 47:
    logger.warning(f"結合後の行数が47ではありません。都道府県名の表記ゆれを確認してください。")
    # 結合できなかった都道府県を特定
    merged_prefs = set(df_analysis["prefecture"])
    dental_prefs = set(df_dental["prefecture"])
    hba1c_prefs = set(df_outcomes["prefecture"])
    logger.warning(f"歯科データにのみ存在: {dental_prefs - merged_prefs}")
    logger.warning(f"HbA1cデータにのみ存在: {hba1c_prefs - merged_prefs}")

# ========================================
# Step 6: 欠損値確認
# ========================================
logger.info(f"欠損値:\n{df_analysis.isna().sum()}")
logger.info(f"基本統計:\n{df_analysis.describe()}")

# ========================================
# Step 7: 保存
# ========================================
output_path = os.path.join(INTERIM_DIR, config["output"]["files"]["analysis_dataset"])
df_analysis.to_csv(output_path, index=False, encoding="utf-8")
logger.info(f"解析用データセット保存完了: {output_path}")
logger.info(f"最終カラム: {df_analysis.columns.tolist()}")
logger.info("Phase 2 完了")
