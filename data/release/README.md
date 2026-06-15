# data/release/ — Aggregated Release Dataset

## Overview

This directory contains the aggregated prefecture-level dataset used in all
analyses reported in:

> Saito H, et al. "Geographic Association between Periodontal Disease Burden
> and Diabetes Complication Management Rates in Japan: An Ecological Study
> Using the National Database of Health Insurance Claims." [Journal, Year].

## Files

| File | Description |
|------|-------------|
| `dental_prefecture_analysis_dataset.csv` | Main analysis dataset (N=47) |
| `variable_dictionary.json` | Variable definitions, units, and data sources |
| `README.md` | This file |

## Dataset Description

- **Unit of analysis**: Prefecture (都道府県), N=47
- **Coverage**: All 47 prefectures of Japan
- **Time period**: FY2023 receipts (FY2022 for specific health checkup variables)

## Quick Start

```python
import pandas as pd
df = pd.read_csv("dental_prefecture_analysis_dataset.csv")
print(df.shape)  # (47, 9)
print(df.describe())
```

## License

This dataset is released under CC BY 4.0.
See `../../LICENSE-DATA` for full license text.

## Citation

When using this dataset, please cite:
```
Saito H, et al. (2026). Geographic Association between Periodontal Disease Burden
and Diabetes Complication Management Rates in Japan: An Ecological Study Using the
National Database of Health Insurance Claims. [Journal].
https://doi.org/[TBD]

Dataset: https://doi.org/10.5281/zenodo.[TBD]
```

## Data Sources

See `../../DATA_SOURCES.md` for full details on primary data sources (NDB Open Data,
Statistics Bureau of Japan, National Tax Agency).
