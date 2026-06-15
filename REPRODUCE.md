# Reproducibility Guide

## Overview

This repository contains the reproducible code and aggregated data for:

> Saito H, et al. "Geographic Association between Periodontal Disease Burden
> and Diabetes Complication Management Rates in Japan: An Ecological Study
> Using the National Database of Health Insurance Claims."

## Environment Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

**Python version**: 3.10 or higher recommended.

## Data

The aggregated prefecture-level dataset (N=47) required to reproduce all
analyses is included in `data/release/`:

```
data/release/
├── dental_prefecture_analysis_dataset.csv   # Main analysis dataset (N=47)
├── variable_dictionary.json                  # Variable definitions and units
└── README.md                                 # Dataset description and citation
```

> Note: Raw NDB Open Data (Excel files) are not redistributed here due to file size.
> See DATA_SOURCES.md for download instructions.

## Execution Order

Run scripts in the following order to reproduce all results:

```bash
# Step 1: Extract periodontal disease data from NDB Open Data
python 03_Analysis/analysis/01_extract_dental_data.py

# Step 2: Integrate analysis dataset (periodontal + diabetes complication rates)
python 03_Analysis/analysis/02_integrate_dataset.py

# Step 3: Add smoking and BMI covariates from NDB specific health checkup data
python 03_Analysis/analysis/02b_add_smoking_bmi.py

# Step 4: Main regression analysis (OLS + sensitivity analyses)
python 03_Analysis/analysis/03_regression_analysis.py

# Step 5: Additional sensitivity analyses (E-value, negative control)
python 03_Analysis/analysis/03b_additional_sensitivity.py

# Step 6: Main figures (scatter plots, forest plots, choropleth maps, LISA)
python 03_Analysis/analysis/04_visualization.py

# Step 7: Additional figures (DAG, mediation path diagram)
python 03_Analysis/analysis/04b_additional_figures.py

# Step 8: Mediation analysis (periodontal → HbA1c → diabetes complication)
python 03_Analysis/analysis/05_mediation_analysis.py
```

> If starting from `data/release/dental_prefecture_analysis_dataset.csv`,
> begin from Step 4 (skip Steps 1-3).

## Expected Outputs

| File | Description |
|------|-------------|
| `03_Analysis/results/regression_results.csv` | Main OLS regression results |
| `03_Analysis/results/sensitivity_analysis_results.csv` | Sensitivity analyses (6 specifications) |
| `03_Analysis/results/negative_control_results.csv` | Negative control outcomes |
| `03_Analysis/results/evalue_results.csv` | E-value analysis results |
| `03_Analysis/results/figures/scatter_periodontal_dm_complication_rate.png` | Figure 1: Scatter plot |
| `03_Analysis/results/figures/forest_plot_dm_complication_rate.png` | Figure 2: Forest plot |
| `03_Analysis/results/figures/forest_plot_negative_control.png` | Figure 3: Negative control forest plot |
| `03_Analysis/results/figures/choropleth_periodontal_rate.png` | Figure 4: Choropleth map |
| `03_Analysis/results/figures/lisa_cluster_map.png` | Figure 5: LISA cluster map |

## Manuscript

The Quarto source file for the manuscript is at:
```
04_Manuscripts/Manuscript_dental_systemic.qmd
```

To render:
```bash
quarto render 04_Manuscripts/Manuscript_dental_systemic.qmd --to docx
quarto render 04_Manuscripts/Manuscript_dental_systemic.qmd --to html
```

## Citation

If you use this code or data, please cite using the metadata in `CITATION.cff`.
