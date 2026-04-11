# 生成AI・エージェント利用開示（論文別）

> 本ファイルは [00_Docs/templates/AI_USE_DISCLOSURE.template.md](../../../00_Docs/templates/AI_USE_DISCLOSURE.template.md) に基づく。**文献の実在性監査**は別紙 `REFERENCE_AUDIT_LOG_2026-04-07.md` を参照。

---

## メタデータ

| 項目 | 内容 |
|------|------|
| 論文仮題 | 歯周病の都道府県別罹患率と糖尿病指標の生態学的関連 |
| 論文仮題（英語） | Ecological association between periodontal disease prevalence and diabetes indicators across Japanese prefectures |
| プロジェクトパス | `projects/NDB_XXX_dental_systemic/` |
| 対象誌（候補） | Journal of Diabetes Investigation; Journal of Clinical Periodontology; Journal of Epidemiology（[README.md](../README.md) 参照） |
| 最終更新日 | 2026-04-08 |
| 記録責任者 | 通信著者（`Manuscript_dental_systemic.qmd` の YAML `author` と同一人物。投稿前に実名に差し替え） |

---

## 使用ツール一覧

| ツール・サービス | 区分 | モデル・バージョン（分かる範囲） | 主な用途 |
|------------------|------|----------------------------------|----------|
| Cursor | クラウドエージェント（設定依存） | 利用時点のエージェントモデル | 解析スクリプトの生成・修正、Quarto原稿・参考文献整理の支援 |
| LM Studio 等 | ローカル | — | **未使用**（総当たりスクリーニング線を採用せず、`research_screening_kit` 経由の Gemma 意味付けも実施なし） |

**注**: AIを著者・共著者として記載しない。最終責任は人間の著者が負う。

---

## 研究段階別の利用

プロジェクトの Phase 1〜5（[README.md](../README.md)）に対応して追記する。

### 1. データ整備・ETL・スクリプト生成

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| 2026-04-06 | Cursor 等 | Phase1 歯科傷病抽出（`01_extract_dental_data.py`）の生成・実行 | `logs/phase1_extract.log` |
| 2026-04-06 | Cursor 等 | Phase2 パネル結合（`02_integrate_dataset.py`） | `logs/phase2_integrate.log` |
| 2026-04-07 | Cursor 等 | Phase2b 喫煙率・BMI 肥満率の統合（`02b_add_smoking_bmi.py`） | `logs/phase2b_smoking_bmi.log` |

### 2. 探索的スクリーニング／ローカルLLMによる意味付け（該当研究のみ）

**本プロジェクト**: 単一仮説・直線パイプライン（Phase 1〜5）であり、`research_screening_kit` による曝露×アウトカム総当たりスクリーニング線は主対象としていない。

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| — | — | **該当なし** | 曝露×アウトカム総当たりスクリーニング・ローカル LLM 意味付けは未実施 |

### 3. 確証的分析・可視化・感度分析

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| 2026-04-06 | Cursor 等 | Phase3 回帰・Moran's I・負の対照等（`03_regression_analysis.py`） | `logs/phase3_regression.log` |
| 2026-04-06 | Cursor 等 | Phase4 主要図表（`04_visualization.py`） | `logs/phase4_visualization.log` |
| 2026-04-07 | Cursor 等 | Phase3b 追加感度（所得・喫煙・BMI、Spec8-10 等）（`03b_additional_sensitivity.py`） | `logs/phase3b_additional.log` |
| 2026-04-07 | Cursor 等 | Phase5 媒介分析（`05_mediation_analysis.py`） | `logs/phase5_mediation.log` |
| 2026-04-07 | Cursor 等 | Phase4b 追加図（四分位・拡張 Forest 等）（`04b_additional_figures.py`） | `logs/phase4b_figures.log` |
| 2026-04-08 | Cursor 等 | `03b` の E-value 用 Spec1 行選択バグ修正・`evalue_results.csv` 再生成・図の再出力 | `NUMBERS_VERIFICATION.md` |

### 4. 原稿（構成・下書き・英訳・推敲・形式調整）

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| 2026-04-06〜2026-04-08 | Cursor 等 | `Manuscript_dental_systemic.qmd` の構成・英文・Abstract/Discussion の推敲・追記 | 解析結果更新に伴う本文修正を含む |

### 5. 参考文献・引用番号の整理

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| 2026-04-06〜2026-04-07 | Cursor 等 | 引用整合・`references.bib` 整備の支援 | 実在性検証は `REFERENCE_AUDIT_LOG_2026-04-07.md`（監査基準日 2026-04-06） |

---

## データ境界（クラウドに送らなかったもの／送ったもの）

### 外部クラウドLLMに**送らなかった**もの

- [x] NDB 生データ（`02_Data/raw/`）の実数値・スクリーンショット（方針として禁止・`.cursorignore` 推奨）
- [x] CIRCS 個票（本プロジェクトの主解析は NDB オープンデータ線）
- [x] 再識別リスクの高い細かい集計の丸貼り

### 送ったもの（機微度が低いと判断した範囲）

| 種別 | 例 |
|------|-----|
| メタデータ・コード | 列名、スキーマ、スクリプト、パス、ダミー行 |
| 原稿・解説 | IMRAD 下書き、既に公開レベルの集計の叙述（数値は出力ファイルと照合） |

### ローカルLLMに入力したもの（該当時）

| 種別 | 例 |
|------|-----|
| — | **該当なし**（本プロジェクトでは未使用） |

---

## 人間による検証

| 段階 | 確認内容 | 実施者 | 日付 |
|------|----------|--------|------|
| コード | 各 Phase スクリプトのローカル実行とログ・出力の確認 | 著者（YAML の `author` と同一） | 2026-04-06〜2026-04-07（ログタイムスタンプに整合） |
| 数値 | 本文・表と `03_Analysis/results/` の一致 | 同上 | 2026-04-08：`NUMBERS_VERIFICATION.md` 記録済み（改稿のたびに再確認） |
| 引用 | PubMed 等による文献実在性（監査ログ参照） | 同上 | 監査基準日 2026-04-06（`REFERENCE_AUDIT_LOG_2026-04-07.md`） |
| 解釈 | 生態学研究の限界・因果の取り扱い | 同上 | 原稿執筆期間中（継続） |

---

## 投稿用短文ドラフト

### 日本語（案）

本研究の原稿作成および解析コードの整備において、Cursor 等のコーディング支援環境（生成AIエージェント）を用いた。統計手法の選定、結果の解釈、結論、および参考文献の最終選択は著者が行い、生成されたコードおよび文章の正確性を著者が検証した。AIは著者として記載していない。

### English (draft)

The authors used AI-assisted coding and writing tools (e.g., Cursor) to support manuscript preparation and analysis scripting. The authors were solely responsible for the selection of statistical methods, interpretation of findings, conclusions, and final reference list, and verified all AI-assisted code and text. AI was not listed as an author.

---

## 変更履歴

| 日付 | 変更内容 |
|------|----------|
| 2026-04-08 | 初版（テンプレート準拠） |
| 2026-04-08 | 解析ログ日付に基づき段階別・検証欄を具体化 |
| 2026-04-08 | 投稿準備：数値照合・E-value 出力修正・`REFERENCE_AUDIT_LOG` §7 追記 |
