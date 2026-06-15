"""
create_zenodo_bundle.py
-----------------------
論文で言及・参照されているファイルのみを収録した Zenodo 公開用 ZIP を生成する。

内部メモ・改訂版 DOCX・探索スクリプト等は一切含まない。
実行後に生成される NDB_XXX_dental_systemic_zenodo_v1.0.0.zip を
Zenodo の手動アップロード画面でアップロードすること。
"""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_ZIP = ROOT / "NDB_XXX_dental_systemic_zenodo_v1.0.0.zip"
PREFIX = "NDB_XXX_dental_systemic-v1.0.0"  # zip 内のルートフォルダ名

# ============================================================
# 収録ファイル ホワイトリスト（論文で言及・参照されるもののみ）
# ============================================================
INCLUDE_FILES = [
    # ── リポジトリルート ──────────────────────────────────
    "CITATION.cff",
    "LICENSE",
    "LICENSE-DATA",
    "README.md",
    "REPRODUCE.md",
    "DATA_SOURCES.md",
    "requirements.txt",

    # ── 公開リリースデータ（N=47、論文 Data Availability 記載） ──
    "data/release/README.md",
    "data/release/dental_prefecture_analysis_dataset.csv",
    "data/release/variable_dictionary.json",

    # ── 解析スクリプト（論文 Methods・Data Availability 記載） ──
    "03_Analysis/analysis/01_extract_dental_data.py",
    "03_Analysis/analysis/02_integrate_dataset.py",
    "03_Analysis/analysis/02b_add_smoking_bmi.py",
    "03_Analysis/analysis/03_regression_analysis.py",
    "03_Analysis/analysis/03b_additional_sensitivity.py",
    "03_Analysis/analysis/04_visualization.py",
    "03_Analysis/analysis/04b_additional_figures.py",
    "03_Analysis/analysis/05_mediation_analysis.py",
    "03_Analysis/analysis/prefecture_labels_en.py",

    # ── 解析結果（論文 Table・Figure 相当） ───────────────
    "03_Analysis/results/regression_results.csv",
    "03_Analysis/results/sensitivity_analysis_results.csv",
    "03_Analysis/results/negative_control_results.csv",
    "03_Analysis/results/evalue_results.csv",

    # ── 論文掲載図（Figure 1-5 相当） ─────────────────────
    "03_Analysis/results/figures/scatter_periodontal_dm_complication_rate.png",  # Figure 1
    "03_Analysis/results/figures/forest_plot_dm_complication_rate.png",           # Figure 2
    "03_Analysis/results/figures/forest_plot_negative_control.png",               # Figure 3
    "03_Analysis/results/figures/choropleth_periodontal_rate.png",                # Figure 4
    "03_Analysis/results/figures/lisa_cluster_map.png",                           # Figure 5

    # ── 論文本体（Quarto ソース・参考文献・CSL） ──────────
    "04_Manuscripts/Manuscript_dental_systemic.qmd",
    "04_Manuscripts/references.bib",
    "04_Manuscripts/vancouver.csl",
    "04_Manuscripts/AI_USE_DISCLOSURE.md",
]


def main() -> None:
    missing = []
    included = []

    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in INCLUDE_FILES:
            src = ROOT / rel
            if src.exists():
                zf.write(src, f"{PREFIX}/{rel}")
                included.append(rel)
            else:
                missing.append(rel)

    print(f"\n[OK] Included ({len(included)} files):")
    for f in included:
        print(f"   {f}")

    if missing:
        print(f"\n[WARN] Not found ({len(missing)} files):")
        for f in missing:
            print(f"   {f}")

    size_mb = OUT_ZIP.stat().st_size / 1024 / 1024
    print(f"\nOutput: {OUT_ZIP.name}  ({size_mb:.1f} MB)")
    print("-> Upload this file to Zenodo (https://zenodo.org/uploads/new).")


if __name__ == "__main__":
    main()
