# 参考文献監査ログ（PubMed実在性検証）

- 対象ファイル: `projects/NDB_XXX_dental_systemic/04_Manuscripts/references.bib`
- 対象本文: `projects/NDB_XXX_dental_systemic/04_Manuscripts/Manuscript_dental_systemic.qmd`
- 監査基準日: **2026-04-06 (JST)**
- 判定ルール: 公開・索引が基準日以前であることを確認のうえ、DOI／PMID／出版社情報で実在を裏付けたものを `OK` とする（政策文書等は公式サイトを一次根拠とする）

## 1) 本文で使用している現行キーと書誌上の位置づけ

| キー | 役割（本文での用い方） | 根拠の種類 | PMID / DOI | 基準日判定 |
|---|---|---|---|---|
| `kassebaumGlobalBurdenSevere2014` | 世界の重度歯周病負担 | 査読原著 | PMID: 25261053 / DOI: 10.1177/0022034514552491 | OK |
| `takahashiTemporalTrendsPrevalence2019` | 日本の成人における歯周病有病の記述 | 査読原著 | PMID: 32075622 / DOI: 10.1186/s12903-020-1046-4 | OK |
| `tairaRegionalInequalityDental2021` | NDBに基づく歯科医療利用の地域差 | 査読原著 | PMID: 34527966 / DOI: 10.1016/j.lanwpc.2021.100170 | OK（キー名修正済: 260604） |
| `chappleDiabetesPeriodontalDiseases2013` | 糖尿病と歯周病の合意報告 | 査読原著 | PMID: 23627322 / DOI: 10.1111/jcpe.12077 | OK |
| `sanzScientificEvidenceLinks2018` | 糖尿病と歯周病のエビデンス・ガイドライン | 査読原著 | PMID: 29280174 / DOI: 10.1111/jcpe.12808 | OK |
| `mealeyDiabetesMellitusPeriodontal2007` | 糖尿病と歯周病の病態・機序の概説 | 査読原著 | PMID: 17474930 / DOI: 10.1111/j.1600-0757.2006.00193.x | OK |
| `iwamotoEffectAntimicrobialPeriodontal2001` | 歯周治療と炎症・HbA1c | 査読原著 | PMID: 11453240 / DOI: 10.1902/jop.2001.72.6.774 | OK |
| `wuPeriodontitisSystemicDiseases2026` | 歯周病と全身疾患のレビュー | 査読原著 | PMID: 41890752 / DOI: 10.3389/fimmu.2026.1777955 | OK |
| `duRoleHbA1cBidirectional2025` | HbA1cと双方向関係のナラティブレビュー | 査読原著 | PMID: 40599550 / DOI: 10.3389/fnut.2025.1606223 | OK |
| `teeuwEffectPeriodontalTreatment2010` | 歯周治療と血糖コントロール（メタ） | 査読原著 | PMID: 20103557 / DOI: 10.2337/dc09-1378 | OK |
| `simpsonTreatmentPeriodontalDisease2015` | Cochraneレビュー（血糖） | 査読レビュー | PMID: 26545069 / DOI: 10.1002/14651858.CD004714.pub3 | OK |
| `umezakiRolePeriodontalTreatment2025` | 歯周治療とHbA1c（メタ） | 査読原著 | PMID: 40070580 / DOI: 10.3389/fcdhc.2025.1541145 | OK |
| `engebretsonEffectNonsurgicalPeriodontal2013` | 大規模RCT（HbA1c非効果） | 査読原著 | PMID: 24346989 / DOI: 10.1001/jama.2013.282431 | OK |
| `belloStatusCareEnd2019` | 世界のESKDケア容量・有病の国際横断 | 査読原著 | PMID: 31601586 / DOI: 10.1136/bmj.l5873 | OK |
| `thurlowGlobalEpidemiologyEnd2021` | ESKDの世界的疫学とKRT格差 | 査読レビュー | PMID: 33752206 / DOI: 10.1159/000514550 | OK |
| `hanafusaAnnualDialysisDataReport2025` | 日本の透析患者登録（JSDT JRDR）年次統計 | 査読原著（公式登録報告） | DOI: 10.1186/s41100-025-00646-3 | OK |
| `mhlwNDBOpenData2024` | NDBオープンデータの出典 | 政府公開資料 | URL: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html / accessed 2026-06-04 | OK（URL・アクセス日追加済: 260604） |
| `wakasugiRegionalVariationDialysis2023` | 日本の都道府県レベルの腎代替療法関連の地域差 | 査読原著 | PMID: 36209260 / DOI: 10.1007/s10157-022-02284-z | OK（キー名修正済: 260604） |
| `lipsitchNegativeControlsTool2010` | 負の対照の考え方 | 査読原著 | PMID: 20335814 / DOI: 10.1097/EDE.0b013e3181d61eeb | OK |
| `whiteHeteroskedasticityConsistentCovariance1980` | HC頑健分散（White） | 査読原著 | DOI: 10.2307/1912934 | OK（PubMed非収載） |
| `vanderweeleSensitivityAnalysisObservational2017` | E-value | 査読原著 | PMID: 28693043 / DOI: 10.7326/M16-2607 | OK |
| `imaiGeneralApproachCausal2010` | 媒介分析の一般枠組み | 査読原著 | PMID: 20954780 / DOI: 10.1037/a0020761 | OK |
| `anselinLocalIndicatorsSpatial1995` | LISA（Moran） | 査読原著 | DOI: 10.1111/j.1538-4632.1995.tb00338.x | OK（PubMed非収載） |
| `anselinSpatialEconometricsMethods1988` | 空間計量の古典書籍 | 書籍 | DOI: 10.1007/978-94-015-7799-1 | OK（PubMed非収載） |
| `kusamaPeriodontalCareLower2025` | 日本DB：歯周ケアと透析開始 | 査読原著 | PMID: 39757133 / DOI: 10.1111/jcpe.14105 | OK |
| `mikamiPeriodontitisRenalFunction2025` | 歯周病重症度とeGFR低下 | 査読原著 | PMID: 41272159 / DOI: 10.1038/s41598-025-25309-5 | OK |
| `rajaDiabeticFootUlcer2023` | 糖尿病性足病変のレビュー | 査読レビュー | PMID: 36970004 / DOI: 10.12998/wjcc.v11.i8.1684 | OK |
| `nishideIncomeRelatedInequalitiesAccess2017` | 日本の歯科アクセスの所得格差 | 査読原著 | PMID: 28498342 / DOI: 10.3390/ijerph14050524 | OK |
| `takeuchiUniversalHealthCheckups2024` | 健診参加と糖尿病・高血圧リスク | 査読原著 | PMID: 39705032 / DOI: 10.1001/jamanetworkopen.2024.51813 | OK |
| `ichidaSocialCapitalIncome2009` | 日本の地域社会資本・健康 | 査読原著 | DOI: 10.1016/j.socscimed.2009.05.006 | OK（PMIDはbibでは管理せず、DOIで照合） |
| `hartInverseCareLaw1971` | Inverse care law | 査読原著 | PMID: 4100731 / DOI: 10.1016/s0140-6736(71)92410-x | OK |
| `matsuyamaSchoolBasedFluorideMouth2016` | 学校フッ素含嗽と都道府県間格差 | 査読原著 | PMID: 27108752 / DOI: 10.2188/jea.JE20150255 | OK |

## 2) メタデータ整備の要点（bib側）

- **PMIDの再照合**: 複数エントリについて、PubMedの正規レコードに合わせて `pmid` を更新した。
- **書誌の差し替え**: 日本の歯科地域格差・腎疾患の地域差・成人歯周病有病など、本文主張と一致する査読文献へ差し替えた。
- **透析統計**: 無効だったDOIに代わり、Crossrefで解決可能な JSDT JRDR の年次報告DOIを採用し、キー名を実態に合わせて整理した（`hanafusaAnnualDialysisDataReport2025`）。
- **国際比較**: 「透析有病の国際的なばらつき」と「日本の位置づけ」を支えるため、国際横断調査および疫学レビューを追加した（`belloStatusCareEnd2019`, `thurlowGlobalEpidemiologyEnd2021`）。
- **重複回避**: 同一主張を担う重複エントリは bib から除き、本文では一本化した。

## 3) 本文（qmd）側の編集方針

- **Introduction**: 国内の歯周病記述を、採用した日本データ文献の内容に整合する表現に調整した。
- **透析負担**: 国際比較文献と日本の登録統計を併記し、断定を避けつつ根拠を明示した。
- **地域格差（歯科）**: 同一テーマの引用を、NDBに基づく査読論文へ統一した。

## 4) 監査サマリー

- 本文で使用するユニークな引用キー数: **32**
- `qmd` 参照キー欠落: **0**
- `references.bib` の重複DOI: **0**
- bib に存在するが本文未使用のエントリ: **4**（`demmerInfluenceType1Type22012`, `saeediGlobalRegionalDiabetes2019`, `winningPeriodontitisSubsequentType2017`, `wuPeriodontalDiseaseRisk2021`）

## 5) 文献番号（Vancouver・初登場順）の確認

- **設定**: `Manuscript_dental_systemic.qmd` で `csl: vancouver.csl` を使用。
- **確認方法**: レンダリング済み `Manuscript_dental_systemic.html` について、(1) 各 `<span class="citation">` ブロック内の `href="#ref-…"` と番号の対応を取得し、(2) en-dash で中間文献が省略されている箇所は `data-cites` の順と番号の等差で中間番号を補完し、(3) 本文先頭から初めて現れる順に割り当て番号が単調非減少であることを検証した。
- **結果**: **32キーすべてについて番号が一意に割り当てられ、初登場順に沿った単調非減少であることを確認した（違反0件）。**
- **注記**: 同一括弧内で Vancouver 体裁により **番号が昇順に並べ替えて表示** される場合がある（例: 初出が後のキーでも `(8,27)` のように表示）。これは **番号の割当順序の誤りではなく、スタイル上の並べ替え** である。
- **再確認（最終レンダリング後）**: `Manuscript_dental_systemic.html` に対する再検証でも、`unique=32`, `violations=0`, `first=kassebaumGlobalBurdenSevere2014#1`, `last=matsuyamaSchoolBasedFluorideMouth2016#32` を確認した。

## 6) 備考

- 政策資料（`mhlwNDBOpenData2024`）はPubMed収載対象外のため、公式サイトを一次ソースとして維持する。
- `ichidaSocialCapitalIncome2009` はDOIで実在を確認し、bibではPMIDに依存しない運用とした（将来、PubMed索引の変化があれば再照合推奨）。

## 7) 投稿前再確認（2026-04-08）

- **キー整合**: `Manuscript_dental_systemic.qmd` 内の `@cite` キー（32 件）を `references.bib` と突合し、**bib 欠落 0** を確認（ローカルスクリプトによる抽出）。
- **未引用 bib**: §4 記載の 4 エントリは現状維持（将来の改稿用に残す場合は可）。
- **数値パイプライン**: `03b_additional_sensitivity.py` の Spec1 行選択を `Spec1_Baseline` 固定に修正し `evalue_results.csv` を再生成。本文・図との対応は `NUMBERS_VERIFICATION.md` を参照。
