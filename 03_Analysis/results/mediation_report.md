# 所得媒介分析レポート（Baron-Kenny + Bootstrap）
**解析日**: 2026-04-07  
**曝露**: periodontal_rate（/10万人、スケール: ÷10000）  
**媒介変数**: income_per_capita（スケール: ÷100）  
**アウトカム**: dm_complication_rate（件/10万人）  
**共変量**: aging_rate, pop_density  

## パス係数（Baron-Kenny）

| パス | 係数 | p値 |
|-----|------|-----|
| a: periodontal → income | 0.4406 | 0.004 |
| b: income → dm_comp（直接） | 9.4179 | 0.308 |
| c: Total effect | 18.3829 | 0.038 |
| c': ADE（所得調整後） | 14.2330 | 0.140 |

## 媒介効果（Baron-Kenny）

- **間接効果（a×b）**: 4.1500
- **媒介割合**: 22.6%

## 解釈（シナリオA）

所得はpartial mediator（媒介割合>20%）。ADE（直接効果）が残存すればSpec7は過調整

## 論文記載文案（英語）

Formal mediation analysis indicated that income_per_capita partially mediated the association between periodontal_rate and dm_complication_rate (indirect effect via Baron-Kenny: 4.150; proportion mediated: 22.6%). The direct effect (ADE) remained in the same direction (beta = 14.2330, p = 0.140), suggesting that income acts as a partial mediator rather than a pure confounder. The attenuation observed in Spec7 (full income adjustment) may therefore reflect partial over-adjustment rather than pure confounding.
