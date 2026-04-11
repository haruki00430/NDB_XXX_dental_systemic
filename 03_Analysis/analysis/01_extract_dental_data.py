"""
Phase 1: 歯科傷病データ抽出
NDB Open Data No.10「04_歯科傷病/都道府県別_傷病件数.xlsx」から
歯周炎（コード5234009）・う蝕（コード8843836）の都道府県別件数を抽出する。

【ファイル構造の注意】
  このファイルは「疾患が行・都道府県が列」の転置構造。
  行: 各疾患（コード・名称・合計・都道府県01-47）
  列4以降: 都道府県コード(01-47) with 都道府県名をMultiIndex

出力: 02_Data/interim/dental_disease_prefecture.csv
"""
import os
import sys
import pandas as pd
import numpy as np
import yaml
import logging

# パス設定
PROJECT_ROOT = "C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub"
PROJECT_DIR = os.path.join(PROJECT_ROOT, "projects", "NDB_XXX_dental_systemic")
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from ndb_library.utils import clean_numeric
from ndb_library.logger import setup_logger

os.makedirs(os.path.join(PROJECT_DIR, "03_Analysis", "analysis", "logs"), exist_ok=True)
logger = setup_logger(__name__, log_file=os.path.join(PROJECT_DIR, "03_Analysis", "analysis", "logs", "phase1_extract.log"))

with open(os.path.join(PROJECT_DIR, "config", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

NDB_ROOT = config["data_sources"]["ndb_root"]
OUTPUT_DIR = os.path.join(PROJECT_DIR, config["output"]["interim_dir"])
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========================================
# 対象疾患コード定義
# ========================================
# 歯周炎 (ICD-10: K05.2-K05.4 相当、NDBコード: 5234009)
# う蝕 (ICD-10: K02 相当、NDBコード: 8843836)
TARGET_CODES = {
    "5234009": "periodontal",   # 歯周炎（主解析）
    "5234016": "chronic_periodontal",  # 慢性歯周炎（感度分析）
    "8843836": "caries",        # う蝕（感度分析）
}

# 都道府県コード → 都道府県名 マッピング
PREF_CODE_MAP = {
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

# ========================================
# Step 1: Excelを header=[2,3] で読み込む
# ========================================
dental_path = os.path.join(NDB_ROOT, config["data_sources"]["dental_disease"]["path"])
logger.info(f"読み込み: {dental_path}")

df = pd.read_excel(dental_path, header=[2, 3])
logger.info(f"データサイズ: {df.shape}  （行=疾患数、列=4メタ列+47都道府県列）")

# ========================================
# Step 2: 列構造の確認とコードカラムの特定
# ========================================
# MultiIndex 構造:
#   列0: (傷病グループ系, ..., '傷病グループ')
#   列1: (..., '疾患コード')
#   列2: (..., '疾患名')
#   列3: (..., '計(傷病件数)')
#   列4-50: (都道府県コード01-47, 都道府県名)

# 列のMultiIndexレベル0（上段）を確認
cols_l0 = [str(c[0]) if isinstance(c, tuple) else str(c) for c in df.columns]
cols_l1 = [str(c[1]) if isinstance(c, tuple) else str(c) for c in df.columns]

logger.info("先頭10列 (level0 | level1):")
for i in range(min(10, len(df.columns))):
    logger.info(f"  列{i}: '{cols_l0[i]}' | '{cols_l1[i]}'")

# 都道府県コード列の特定（level0が '01'〜'47'）
pref_cols = {}
for i, (l0, l1) in enumerate(zip(cols_l0, cols_l1)):
    code_str = l0.strip() if l0.strip().isdigit() else None
    if code_str and 1 <= int(code_str) <= 47:
        pref_code = code_str.zfill(2)
        pref_cols[pref_code] = i  # コード → 列番号

logger.info(f"都道府県列数: {len(pref_cols)} (47であれば正常)")
if len(pref_cols) != 47:
    logger.warning(f"都道府県列数が47ではありません: {len(pref_cols)}")

# ========================================
# Step 3: 疾患コード列の特定
# ========================================
# 疾患コードは列1（level1に「コード」を含む列）
code_col_idx = 1   # 列1 = 疾患コード
name_col_idx = 2   # 列2 = 疾患名
total_col_idx = 3  # 列3 = 合計

# 疾患コード列をstrに変換
df_codes = df.iloc[:, code_col_idx].astype(str).str.strip()

# ========================================
# Step 4: 対象疾患行の抽出
# ========================================
results = {}
for code, var_name in TARGET_CODES.items():
    mask = df_codes == code
    matched = df[mask]

    if len(matched) == 0:
        logger.warning(f"コード {code} ({var_name}) が見つかりませんでした")
        continue
    if len(matched) > 1:
        logger.warning(f"コード {code} が複数行ヒット ({len(matched)}行)。最初の行を使用。")

    row = matched.iloc[0]
    disease_name = str(row.iloc[name_col_idx])
    total_count = row.iloc[total_col_idx]
    logger.info(f"コード {code} → 疾患名: {disease_name}, 全国合計: {total_count}")

    # 各都道府県の件数を取得
    pref_values = {}
    for pref_code, col_idx in pref_cols.items():
        val = row.iloc[col_idx]
        # マスク値（"-"やNaN）→ NaN、数値はfloatへ
        if pd.isna(val) or str(val).strip() == "-":
            pref_values[pref_code] = np.nan
        else:
            try:
                pref_values[pref_code] = float(str(val).replace(",", "").replace("　", ""))
            except (ValueError, AttributeError):
                pref_values[pref_code] = np.nan

    results[var_name] = pref_values
    logger.info(f"  抽出完了: {len(pref_values)}都道府県")

if not results:
    logger.error("いずれの疾患コードも抽出できませんでした。スクリプトを終了します。")
    sys.exit(1)

# ========================================
# Step 5: 都道府県別データフレームの作成
# ========================================
# 都道府県コード → 都道府県名 → 各疾患件数 の行形式に変換
rows = []
for pref_code, pref_name in PREF_CODE_MAP.items():
    row_data = {"prefecture_code": pref_code, "prefecture": pref_name}
    for var_name, pref_values in results.items():
        row_data[f"{var_name}_count"] = pref_values.get(pref_code, np.nan)
    rows.append(row_data)

df_out = pd.DataFrame(rows)
logger.info(f"都道府県データフレーム: {df_out.shape}")
logger.info(f"歯周炎件数の確認 (periodontal_count):\n{df_out['periodontal_count'].describe()}")
logger.info(f"欠損値:\n{df_out.isna().sum()}")

# ========================================
# Step 6: 人口データ結合 → 算定率算出
# ========================================
hba1c_data_path = config["data_sources"]["hba1c_existing"]["path"]
logger.info(f"既存HbA1cデータを読み込みます: {hba1c_data_path}")
df_hba1c = pd.read_csv(hba1c_data_path, encoding="utf-8")
logger.info(f"既存データカラム: {df_hba1c.columns.tolist()}")
logger.info(f"既存データ行数: {len(df_hba1c)}")

df_merged = pd.merge(df_out, df_hba1c[["prefecture", "population", "aging_rate", "pop_density"]],
                     on="prefecture", how="left")
logger.info(f"結合後: {len(df_merged)}行（47であれば正常）")

if df_merged["population"].isna().any():
    missing = df_merged[df_merged["population"].isna()]["prefecture"].tolist()
    logger.warning(f"人口データが取得できなかった都道府県: {missing}")

# 件数率（/人口10万人）算出
for var_name in results.keys():
    count_col = f"{var_name}_count"
    rate_col = f"{var_name}_rate"
    df_merged[rate_col] = df_merged[count_col] / df_merged["population"] * 100000
    logger.info(f"{rate_col} (/10万人) 統計: mean={df_merged[rate_col].mean():.1f}, "
                f"min={df_merged[rate_col].min():.1f}, max={df_merged[rate_col].max():.1f}")

# ========================================
# Step 7: 保存
# ========================================
save_cols = ["prefecture", "prefecture_code"] + \
            [f"{v}_count" for v in results] + \
            [f"{v}_rate" for v in results] + \
            ["population"]

output_path = os.path.join(OUTPUT_DIR, config["output"]["files"]["dental_data"])
df_merged[save_cols].to_csv(output_path, index=False, encoding="utf-8")
logger.info(f"歯科傷病データ保存完了: {output_path}")
logger.info(f"保存行数: {len(df_merged)}")
logger.info("Phase 1 完了")
