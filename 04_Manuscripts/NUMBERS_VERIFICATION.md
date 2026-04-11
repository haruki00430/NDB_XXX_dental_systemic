# 本文数値と解析出力の照合記録

照合日: 2026-04-08  
根拠ファイル: `03_Analysis/results/`（再現実行は `03b_additional_sensitivity.py` で E-value CSV を更新済み）

## 修正した不整合（コード側）

- **`evalue_results.csv`**: `03b_additional_sensitivity.py` が `spec.str.contains("Spec1")` のため **`Spec10` に誤マッチ**し、Spec10 の β で E-value が算出されていた。`specification == "Spec1_Baseline"` に変更し再出力。本文・図（RR ≈ 1.43、E-value ≈ 2.21、CI 下限 E-value ≈ 1.17）と一致。

## 主要数値（突合済み）

| 項目 | 本文（代表） | ソース |
|------|----------------|--------|
| 主解析 β / CI / p / R²（dm complication） | 0.00184, 0.00011–0.00357, 0.038, 0.104 | `regression_results.csv` Spec1_Baseline |
| 感度分析 Spec1–10（dm） | Table 3 と一致 | `sensitivity_analysis_v2.csv` |
| Moran's I（periodontal_rate） | 0.359, p = 0.002, z ≈ 3.53 | `morans_i_results.txt`（I=0.3586, z=3.511 は四捨五入差） |
| LM 検定（dm_complication 残差） | LM-Lag 0.216, LM-Error 0.324 | `phase3_regression.log` |
| E-value（主関連） | RR ≈ 1.43, E ≈ 2.21, CI 下限 E ≈ 1.17 | `evalue_results.csv`（修正後） |
| PAF / 超過件数 | PAF ≈ 8.9%, ≈ 9,700 件/年 | `paf_results.csv` |
| 四分位 Q1/Q4 平均、トレンド p | 171.5 / 238.5, p = 0.132 | `quartile_analysis.csv` |
| 陰性対照（caries → dm、Spec1–6） | いずれも p > 0.70 帯 | `negative_control_results.csv` |
| 媒介（Bootstrap） | ACME 5.11, p = 0.356; ADE 12.34, p = 0.162 | `phase5_mediation.log` / `05_mediation_analysis.py` 出力 |
| Baron–Kenny c'（OLS 結果モデル） | β = 14.23, p = 0.140 | ログ記載（本文の Bootstrap ADE 12.34 とは別指標） |

## 図ファイル

`Manuscript_dental_systemic.qmd` の Figure / Supplementary パスは `results/figures/`（原稿からは `../results/figures/`）以下の PNG と一致。E-value 図は `04b_additional_figures.py` が **Spec1 の固定 β** で描画（`evalue_results.csv` の SD と整合）。

## 表の脚注

- Table 3: 「6/10 が p≤0.054」は Spec4・Spec8 の p がいずれも **0.0542… で 0.054 をわずかに超える**ため不正確。脚注を「5 仕様が p<0.05、Spec4/8 は p≈0.054」の記述に更新済み。

## 次回再実行時

1. `01_extract` → `02_integrate` → `02b` → `03_regression` → `03b` → `04` → `04b` → `05_mediation`（README 参照）
