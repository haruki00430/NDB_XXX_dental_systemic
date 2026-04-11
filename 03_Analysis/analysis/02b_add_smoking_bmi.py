"""
Phase 2b: 喫煙率（Q5）と BMI 肥満率を analysis_dataset_v2.csv に追加

入力:
  - 02_Data/interim/analysis_dataset.csv  ← 既存（14列）
  - NDB Q5 Excel（都道府県別喫煙率）
  - NDB_XXX_chrono_nutrition/data/interim/examination_outcomes.csv（bmi_obesity_rate）

出力:
  - 02_Data/interim/analysis_dataset_v2.csv（16列：+smoking_rate, +bmi_obesity_rate）

注意:
  - Q5 は特定健診受診者ベースの喫煙率（一般人口より低い：推定3.5〜8%）
  - BMI はchrono_nutritionプロジェクトから流用（NDB No.10 同年度）
"""
import os
import sys
import pandas as pd
import numpy as np

PROJECT_ROOT = "C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub"
PROJECT_DIR  = os.path.join(PROJECT_ROOT, "projects", "NDB_XXX_dental_systemic")
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from ndb_library.logger import setup_logger
logger = setup_logger(__name__, log_file=os.path.join(
    PROJECT_DIR, "03_Analysis", "analysis", "logs", "phase2b_smoking_bmi.log"
))

INTERIM_DIR = os.path.join(PROJECT_DIR, "02_Data", "interim")

# ─────────────────────────────────────────
# 1. ベースデータ読み込み
# ─────────────────────────────────────────
base_path = os.path.join(INTERIM_DIR, "analysis_dataset.csv")
df_base = pd.read_csv(base_path, encoding="utf-8")
logger.info(f"ベースデータ読み込み: {len(df_base)}行 × {len(df_base.columns)}列")
logger.info(f"都道府県一覧: {df_base['prefecture'].tolist()}")

# ─────────────────────────────────────────
# 2. Q5 喫煙率の抽出
# ─────────────────────────────────────────
q5_path = os.path.join(
    PROJECT_ROOT,
    "02_Data", "raw", "NDB_OpenData", "No.10",
    "07_特定健診 質問票", "01_公費レセプトを含まないデータ",
    "標準的な質問票（質問項目５） 都道府県別性年齢階級別分布.xlsx"
)

logger.info(f"Q5 Excel 読み込み: {q5_path}")
df_q5 = pd.read_excel(q5_path, header=None)
logger.info(f"Q5 Shape: {df_q5.shape}")

# 行5〜98: 都道府県データ（2行ペア）
# 奇数行 (5,7,9,...,97): 喫煙あり
# 偶数行 (6,8,10,...,98): 受診者合計（全体）
# 行99-100: 全国集計 → 除外
# 列9 = 男性合計、列17 = 女性合計

smoker_rows = df_q5.iloc[5:99:2].reset_index(drop=True)  # 47行（喫煙あり）
total_rows  = df_q5.iloc[6:100:2].reset_index(drop=True) # 47行（受診者合計）

logger.info(f"喫煙あり行数: {len(smoker_rows)}, 受診者合計行数: {len(total_rows)}")

# 都道府県名は smoker_rows の列0
pref_names = smoker_rows[0].tolist()

# 男性・女性の喫煙者数と受診者数を取得（列9=男性合計, 列17=女性合計）
smoker_male   = pd.to_numeric(smoker_rows[9],  errors='coerce')
smoker_female = pd.to_numeric(smoker_rows[17], errors='coerce')
total_male    = pd.to_numeric(total_rows[9],   errors='coerce')
total_female  = pd.to_numeric(total_rows[17],  errors='coerce')

smoking_rate = (smoker_male + smoker_female) / (total_male + total_female) * 100

df_smoking = pd.DataFrame({
    "prefecture":   pref_names,
    "smoking_rate": smoking_rate.values
})

# 欠損確認
n_nan_smoke = df_smoking["smoking_rate"].isna().sum()
logger.info(f"喫煙率 NaN 数: {n_nan_smoke}")
logger.info(f"喫煙率 範囲: {df_smoking['smoking_rate'].min():.2f}% 〜 {df_smoking['smoking_rate'].max():.2f}%")
logger.info(f"喫煙率 平均: {df_smoking['smoking_rate'].mean():.2f}%")

# ─────────────────────────────────────────
# 3. BMI 肥満率の読み込み（chrono_nutrition 流用）
# ─────────────────────────────────────────
bmi_path = os.path.join(
    PROJECT_ROOT, "projects", "NDB_XXX_chrono_nutrition",
    "data", "interim", "examination_outcomes.csv"
)

logger.info(f"BMI データ読み込み: {bmi_path}")
df_bmi_raw = pd.read_csv(bmi_path, encoding="utf-8-sig")
logger.info(f"BMI Shape: {df_bmi_raw.shape}, カラム: {df_bmi_raw.columns.tolist()}")

# analysis_dataset の都道府県のみを残す（left join でマッチしたもののみ）
df_bmi = df_bmi_raw[["prefecture", "bmi_obesity_rate"]].copy()
n_bmi_raw = len(df_bmi)
logger.info(f"BMI 読み込み行数: {n_bmi_raw}")

# ─────────────────────────────────────────
# 4. データ統合
# ─────────────────────────────────────────
df_out = df_base.copy()

# 喫煙率をマージ
df_out = df_out.merge(df_smoking, on="prefecture", how="left")
n_smoke_matched = df_out["smoking_rate"].notna().sum()
logger.info(f"喫煙率マッチ数: {n_smoke_matched}/47")

# BMI 肥満率をマージ
df_out = df_out.merge(df_bmi, on="prefecture", how="left")
n_bmi_matched = df_out["bmi_obesity_rate"].notna().sum()
logger.info(f"BMI マッチ数: {n_bmi_matched}/47")

# ─────────────────────────────────────────
# 5. マッチ失敗の診断
# ─────────────────────────────────────────
unmatched_smoke = df_out[df_out["smoking_rate"].isna()]["prefecture"].tolist()
unmatched_bmi   = df_out[df_out["bmi_obesity_rate"].isna()]["prefecture"].tolist()

if unmatched_smoke:
    logger.warning(f"喫煙率マッチ失敗: {unmatched_smoke}")
    logger.info("Q5 都道府県名一覧:")
    for name in pref_names:
        logger.info(f"  '{name}'")

if unmatched_bmi:
    logger.warning(f"BMI マッチ失敗: {unmatched_bmi}")
    logger.info("BMI 都道府県名一覧:")
    for name in df_bmi["prefecture"].tolist():
        logger.info(f"  '{name}'")

# ─────────────────────────────────────────
# 6. 保存
# ─────────────────────────────────────────
out_path = os.path.join(INTERIM_DIR, "analysis_dataset_v2.csv")
df_out.to_csv(out_path, index=False, encoding="utf-8")
logger.info(f"保存完了: {out_path}")
logger.info(f"最終 Shape: {df_out.shape}（{len(df_out)}行 × {len(df_out.columns)}列）")
logger.info(f"カラム: {df_out.columns.tolist()}")

# 検証サマリー
logger.info("\n===== 記述統計（新規変数） =====")
logger.info(f"smoking_rate  : mean={df_out['smoking_rate'].mean():.2f}, "
            f"SD={df_out['smoking_rate'].std():.2f}, "
            f"range=[{df_out['smoking_rate'].min():.2f}, {df_out['smoking_rate'].max():.2f}]")
logger.info(f"bmi_obesity_rate: mean={df_out['bmi_obesity_rate'].mean():.2f}, "
            f"SD={df_out['bmi_obesity_rate'].std():.2f}, "
            f"range=[{df_out['bmi_obesity_rate'].min():.2f}, {df_out['bmi_obesity_rate'].max():.2f}]")

logger.info("Phase 2b 完了")
