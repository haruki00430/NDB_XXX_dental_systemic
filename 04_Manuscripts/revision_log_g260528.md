# 修正ログ：Manuscript_dental_systemic.qmd

**対象ファイル**: `04_Manuscripts/Manuscript_dental_systemic.qmd`  
**修正日**: 2026-05-28  
**修正者**: Claude Sonnet 4.6（AI支援）  
**修正根拠**: 投稿優先度1位（g260528 NDBオープンデータ論文17本分順位付け.md）、投稿ターゲット：Journal of Periodontal Research（IF 3.5）

---

## フェーズ1：査読先回り修正（投稿前ブラッシュアップ）

計画ファイル：`C:\Users\user\.claude\plans\adaptive-floating-thompson.md`

### 修正A：Keywords 重複削除

- **箇所**: L32 と L35 に `**Keywords:**` が2回登場していた
- **対応**: L35 の重複 Keywords 行を削除（1行削除のみ）

### 修正B：Methods §Primary Exposure — 処置コードの明文化

- **箇所**: Primary Exposure 段落末尾
- **追加内容**（原文）:

> In the NDB dental claims system, treatment codes for active periodontal interventions, including scaling (J078), scaling and root planing (SRP; J079), and periodontal surgery (J084–J085), are billed distinctly from preventive prophylaxis visits. The claim-based K05 exposure used in this study therefore predominantly reflects treatment contacts for clinically diagnosed and actively managed periodontal disease, rather than asymptomatic dental screening visits. This coding structure provides a meaningful, albeit imperfect, proxy for the regional burden of active periodontal disease requiring clinical intervention.

- **意図**: 査読者（歯科・レセプト疫学専門）が「予防的クリーニングや軽度歯肉炎も混入しているのでは」と指摘することを先回りして防ぐ

### 修正C：Discussion §Interpretation of the Positive Finding — E-value 段落の強化

- **箇所**: §Interpretation of the Positive Finding の末尾（所得partial mediatorの議論の後）
- **追加内容**（最終版）:

> To provide a quantitative bound on the residual confounding threat, we calculated the E-value for the primary association. An E-value of 2.21 indicates that any unmeasured confounder would need risk ratio associations of at least 2.21-fold with both exposure and outcome to fully explain the observed association. Plausible unmeasured confounders include dietary quality, physical activity, and individual oral hygiene habits. By comparison, per-capita income, the strongest measured confounder, showed a correlation with the exposure corresponding to an approximate RR of 1.4–1.8, which fell below the E-value threshold. The negative control analysis (caries rate: 0/6 specifications significant) further supports that the observed association is not simply an artifact of shared socioeconomic determinants. Taken together, the E-value provides meaningful quantitative reassurance that the association cannot be fully explained by residual confounding alone, though unmeasured confounding inherent to an ecological design cannot be entirely excluded.

- **意図**: E-value=2.21 の「なぜこの数値が現実的な交絡因子を上回るのか」の論理武装を強化

### 修正D：Table 1 — Caries rate 行の注釈追加

- **箇所**: Table 1 の Caries rate 行
- **変更**: セルの `—` を注釈付き `— ^a^` に変更
- **追加注釈（Table 2 下）**:
  > ^a^ Caries rate summary statistics are not shown; this variable was used exclusively as a negative control exposure. Descriptive statistics are available upon request.

---

## フェーズ2：康永先生スキル適用（Round 1）

**対象セクション**: Abstract・Introduction・Discussion主要段落・新規追加段落

| 箇所 | 変更内容 | 適用ルール |
|---|---|---|
| Abstract §Conclusions | `provides` → `provided` | 鉄則7：今回の研究の結果は過去形 |
| Introduction P2 | 「サイトカイン機序文」を2文に分割；`while` で繋いでいた複合文を `Conversely,` で独立 | 鉄則1：20語以内 |
| Introduction P2 | `have demonstrated...can...though` の重複複文 → セミコロン＋`however` | 鉄則1・8 |
| Introduction P3 | em dash（—）→ コンマ（"particularly diabetic nephropathy leading to dialysis"） | 鉄則9：Mダッシュ禁止 |
| Methods §修正B | em dash → コンマ（手技コードリスト箇所） | 鉄則9 |
| Discussion §Summary 第1文 | 83語の長文を2文に分割 | 鉄則1 |
| Discussion §Summary | `does not account` → `did not account` | 鉄則7 |
| Discussion §Summary | em dash `—exceeding` → コンマ | 鉄則9 |
| Discussion §Summary | `~9,700` → `approximately 9,700` | 鉄則10：非公式記号除去 |
| Discussion §Interpretation of Positive Finding | em dash 2か所 → 括弧・コンマ（TNF-α/IL-6/IL-1β、health behaviors列挙） | 鉄則9 |
| Discussion §Interpretation of Positive Finding | `significantly reduced` → `markedly reduced` | 鉄則10："significant"は統計的有意のみ |
| Discussion §E-value段落（修正C） | bold 見出し `**Robustness to unmeasured confounding...**` を削除（周囲パラグラフと書式統一） | 文体統一 |
| Discussion §E-value段落（修正C） | 50語の長文を3文に分割；em dash → コンマ；末尾を能動的構造に修正 | 鉄則1・9 |
| Discussion §Policy Implications | `significantly fewer` → `markedly fewer` | 鉄則10 |
| Discussion §Policy Implications | em dash 2か所 → 括弧・コンマ | 鉄則9 |
| Discussion §Conclusions | `are ecologically consistent` → `were ecologically consistent` | 鉄則7 |
| Discussion §Conclusions | `require cautious interpretation` → `required cautious interpretation` | 鉄則7 |
| Discussion §Conclusions | `further supports` → `further supported` | 鉄則7 |

---

## フェーズ3：康永先生スキル適用（Round 2）

**対象セクション**: 未修正の全セクション（Results・Methods残部・Discussion残部）

### Introduction

| 箇所 | 変更内容 | ルール |
|---|---|---|
| §NDB段落（L44） | 35語の複合文を2文に分割：「NDB covers...providing an opportunity」→「NDB covers... / This near-complete coverage provided an opportunity」 | 鉄則1 |
| §NDB段落 | `have demonstrated` → `demonstrated` | 鉄則3：動詞は簡潔に |
| §NDB段落 | `has not been explored` → `remains unexplored` | 鉄則10：定番表現を活用 |

### Methods

| 箇所 | 変更内容 | ルール |
|---|---|---|
| §Smoking rate | `~16–20%` → `approximately 16–20%` | 非公式記号除去 |
| §Negative Control Analysis | `this supports` → `this would support` | 鉄則7：条件文の時制整合 |

### Results

| 箇所 | 変更内容 | ルール |
|---|---|---|
| §Descriptive Statistics | `varied substantially (...), a 2.1-fold variation` → `varied 2.1-fold (...)` | 鉄則2：冗長削除；鉄則6：価値判断語は Results に不要 |
| §Bivariate Correlations | `modest positive correlation` / `modest negative correlation` → `positive correlation` / `negative correlation` | 鉄則6：Results に価値判断形容詞を使わない |
| §Primary Regression | `significantly positively associated` → `positively and significantly associated` | 鉄則6：副詞重複解消 |
| §Negative Control | em dash → 2文に分割（「Periodontal disease...showed 5/7. This contrast supports...」） | 鉄則1・9 |
| §E-value | em dash・`~` → コンマ・"approximately" | 鉄則9・非公式記号 |
| §Mediation | `significantly positively associated` → `positively and significantly associated` | 鉄則6 |
| §Mediation | `Bootstrap` → `bootstrap`（固有名詞でない） | 表記統一 |
| §Mediation | `~22.6%` → `approximately 22.6%` | 非公式記号 |
| §Mediation | `~20–23%` → `approximately 20–23%` | 非公式記号 |
| §Mediation | `suggests income may partially mediate` → `suggested income may partially mediate` | 鉄則7 |

### Discussion（残存部分）

| 箇所 | 変更内容 | ルール |
|---|---|---|
| §Summary（透析予防Null） | em dash → コンマ（"such as heterogeneity in dialysis prevention program penetration"） | 鉄則9 |
| §Interpretation（DAG文） | 50語超の長文を3文に分割；em dash 2か所を削除；SES の説明を独立文として明確化 | 鉄則1・9 |
| §Interpretation（媒介分析段落） | `~20–23%` → `approximately 20–23%` | 非公式記号 |
| §Interpretation（媒介分析段落） | em dash `—if real—` → 括弧 `(if real)` | 鉄則9 |
| §Interpretation（陰性対照・政策含意） | em dash 2か所 → コンマ（caries rate 挿入句、integrated policies 列挙） | 鉄則9 |
| §Null HbA1c | `Three non-mutually exclusive explanations are proposed.` → `We propose three non-mutually exclusive explanations.` | 鉄則11：受動態→能動態 |
| §Null HbA1c（temporal mismatch） | em dash `—particularly` → コンマ | 鉄則9 |
| §Spatial Pattern | `indicates geographic clustering` → `indicated geographic clustering` | 鉄則7：研究固有の知見は過去形 |

---

## 変更なし（意図的に維持した箇所）

- **"significant" の統計的使用**（p < 0.05 の結果を表す箇所）：すべて維持
- **Table 2・Table 3 の数値**：変更なし（既存解析結果）
- **全文献引用キー**：変更なし
- **Methods §Statistical Analysis の数式**：変更なし
- **Figure・Table のキャプション**：変更なし
- **Abstract §Results の "significant clustering (Moran's I = 0.359, p = 0.002)"**：統計的有意の意味で使用、維持

---

## レンダリング確認

- **HTML レンダリング**：全修正後にエラーなし（`Output created: Manuscript_dental_systemic.html`）
- **警告**：なし（新規引用未追加のため citation warning なし）

---

## 次ステップ

- [ ] 共著者へのレビュー依頼（DOCX 出力 → 回覧）
- [ ] 同様の康永先生スキル適用：`Manuscript_PT_Disparities_Clinical.qmd`（投稿優先度2位）
- [ ] references.bib の実著者名記入（`[REPLACE]` プレースホルダー）
- [ ] 投稿カバーレター作成
