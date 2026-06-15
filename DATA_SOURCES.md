# Data Sources

## Primary Data

### NDB Open Data (10th Release, FY2023)
- **Provider**: Ministry of Health, Labour and Welfare of Japan (MHLW)
- **URL**: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html
- **Files used**:
  - Dental disease counts (periodontal disease ICD-10: K05): by prefecture, FY2023
  - Diabetes complication management fee (B001-20): by prefecture, FY2023
  - Specific health checkup data: smoking rate, BMI obesity rate, by prefecture, FY2022
- **Access date**: 2025-06

## Covariate Data

### Aging Rate (Proportion of Population Aged ≥65)
- **Provider**: Statistics Bureau of Japan
- **URL**: https://www.e-stat.go.jp/
- **Dataset**: 2020 Population Census
- **Access date**: 2026-03

### Population Density
- **Provider**: Statistics Bureau of Japan
- **URL**: https://www.e-stat.go.jp/
- **Dataset**: 2020 Population Census
- **Access date**: 2026-03

### Income per Capita
- **Provider**: National Tax Agency / e-Stat
- **URL**: https://www.e-stat.go.jp/
- **Dataset**: Prefectural Tax Statistics (municipal taxable income per taxpayer)
- **Access date**: 2026-03
- **Note**: Requires Shift-JIS encoding when reading CSV (cp932)

## Aggregated Release Dataset

The file `data/release/dental_prefecture_analysis_dataset.csv` contains:
- N=47 prefectures
- Periodontal disease rate (B001-2 dental treatment per 100,000 population)
- Diabetes complication management rate (B001-20 per 100,000 population)
- HbA1c high rate (≥7.0%)
- Aging rate, population density, income per capita, smoking rate, BMI obesity rate

This aggregated dataset is derived from the above sources and is released under
CC BY 4.0 (see LICENSE-DATA).

## Notes on Data Availability

- Raw NDB Open Data Excel files are not redistributed in this repository
  (file sizes > 100 MB; freely available from MHLW URL above)
- Specific health checkup data (特定健診): FY2022 (one year prior to receipt data FY2023)
- No individual-level data are included anywhere in this repository
- All analyses use publicly available, pre-aggregated administrative data
