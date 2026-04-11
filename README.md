# NDB_XXX_dental_systemic

## テーマ
**歯周病の都道府県別罹患率と糖尿病指標の生態学的関連**  
Ecological association between periodontal disease prevalence and diabetes indicators across Japanese prefectures

## 研究背景
歯周病（Periodontitis; ICD-10: K05）は慢性炎症性疾患であり、インスリン抵抗性や血糖コントロール悪化を介して2型糖尿病と双方向的な関連を持つことが知られている。しかし、日本全国の都道府県データを用いた生態学的研究は未実施である。NDB Open Data No.10 の歯科傷病データ（04_歯科傷病）と特定健診検査データ（07_特定健診 検査）を用いて、都道府県レベルでの生態学的関連を定量化する。

## 仮説
歯周病罹患率（K05件数/人口10万人）が高い都道府県ほど、HbA1c高値率・糖尿病合併症管理料算定率が高い。

## データソース
| データ | パス | 変数 |
|--------|------|------|
| 歯科傷病（都道府県別） | `02_Data/raw/NDB_OpenData/No.10/04_歯科傷病/01_公費レセプトを含まないデータ/都道府県別_傷病件数.xlsx` | K05（歯周病）・K02（齲蝕）件数 |
| 特定健診検査（HbA1c） | `02_Data/raw/NDB_OpenData/No.10/07_特定健診 検査/...` | HbA1c分布・平均値 |
| 既存HbA1c解析データ | `projects/NDB_XXX_hba1c_complications/data/interim/analysis_dataset_phase1.csv` | hba1c_high_rate, dm_complication_rate等（流用） |

## 解析フロー

```
Phase 1: 歯科傷病データ抽出
  04_歯科傷病 Excel → 都道府県別K05/K02件数 → 人口10万人あたり換算
  → 02_Data/interim/dental_disease_prefecture.csv

Phase 2: 既存HbA1cデータ結合
  既存 analysis_dataset_phase1.csv + dental_disease_prefecture.csv
  → 02_Data/interim/analysis_dataset.csv（47都道府県 × 10+変数）

Phase 3: 統計解析
  OLS回帰（従属変数: HbA1c高値率/合併症率、独立変数: K05件数率）
  感度分析6仕様（Baseline, HC3, Outlier除外, 大都市除外, 交互作用, 対数変換）
  Moran's I（空間的自己相関確認）
  → 03_Analysis/results/

Phase 4: 可視化
  Scatter plot（K05率 vs HbA1c高値率）
  Choropleth map（K05率の都道府県別分布）
  Forest plot（感度分析）

Phase 5: 論文執筆
  → 04_Manuscripts/Manuscript_dental_systemic.qmd

Phase 3b–5（本文の拡張感度・E-value・媒介・追加図）:
  02b: 喫煙・BMI 列を結合 → analysis_dataset_v2.csv
  03b: Spec8–10、E-value、PAF、四分位 → sensitivity_analysis_v2.csv 等
  04b: 四分位バー・拡張 Forest・E-value 図
  05: 所得媒介（Baron–Kenny + Bootstrap）→ mediation_report.md 等
```

## 実行順序（論文と整合する再現パイプライン）

リポジトリルートまたはプロジェクトディレクトリから、**上から順に**実行する。

```bash
python 03_Analysis/analysis/01_extract_dental_data.py   # Phase 1
python 03_Analysis/analysis/02_integrate_dataset.py     # Phase 2（analysis_dataset.csv）
python 03_Analysis/analysis/02b_add_smoking_bmi.py      # Phase 2b → analysis_dataset_v2.csv
python 03_Analysis/analysis/03_regression_analysis.py   # Phase 3（回帰・Moran・陰性対照・Spec1–7 感度）
python 03_Analysis/analysis/03b_additional_sensitivity.py  # Phase 3b（Spec8–10・E-value・PAF・四分位）
python 03_Analysis/analysis/04_visualization.py         # Phase 4（主要図）
python 03_Analysis/analysis/04b_additional_figures.py   # Phase 4b（拡張図・E-value 可視化）
python 03_Analysis/analysis/05_mediation_analysis.py    # Phase 5（媒介分析）
```

投稿用ドキュメント: `04_Manuscripts/Manuscript_dental_systemic.qmd` を `quarto render ... --to docx` で DOCX 化。数値照合メモは `04_Manuscripts/NUMBERS_VERIFICATION.md`。

## 主要アウトカム変数
- `hba1c_high_rate`: HbA1c ≥6.5%の割合（%）
- `dm_complication_rate`: 糖尿病合併症管理料（B001-20）算定率（/10万人）
- `dialysis_prevention_rate`: 糖尿病透析予防指導管理料（B001-27）算定率（/10万人）

## 曝露変数
- `periodontal_rate`: K05（歯周病）件数 / 人口10万人
- `caries_rate`: K02（齲蝕）件数 / 人口10万人（感度分析用）

## 調整変数
- `aging_rate`: 高齢化率（%）
- `pop_density`: 人口密度（人/km²）

## 投稿候補
- Journal of Diabetes Investigation（IF ~3.0）
- Journal of Clinical Periodontology（IF ~5.0）
- Journal of Epidemiology（IF ~2.9）
