# STI and HIV Syndemic Burden — Geospatial Co-clustering and Behavioural Determinants in Ghana

[![CI](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

This repository contains all analytical code, data pipeline scripts, and interactive visualisations supporting the manuscript:

> Ghanem VG. *STI and HIV syndemic burden: geospatial co-clustering and behavioural determinants in Ghana.* 2026. (Submitted.)

The study quantifies the spatial co-distribution of sexually transmitted infections (STIs) and HIV across all **260 health districts** of Ghana, identifies behavioural determinants using XGBoost with SHAP interpretability, and translates findings into district-level policy recommendations.

---

## Key Findings

| Metric | Value |
|--------|-------|
| HIV Global Moran I | 0.768 (p < 0.001) |
| STI Global Moran I | 0.514 (p < 0.001) |
| Bivariate LISA (HIV x STI) Moran I | 0.497 (p = 0.001) |
| Bivariate HH hotspot districts | 35 |
| Syndemic Overlap Index | 0.331 (86/260 districts) |
| XGBoost Spatial CV AUC | 0.972 +/- 0.031 |
| Spatial Lag Regression R2 | 0.684 |
| Optimal K-means clusters | 4 (silhouette = 0.234) |

---

## Repository Structure

```
sti-hiv-syndemic-ghana-260districts/
├── src/
│   ├── build_dataset_and_analysis.py   # Master pipeline: data -> spatial stats -> ML -> outputs
│   └── generate_figures.py             # Figure generation (300 DPI PNG + SVG)
├── data/
│   ├── master_260district.csv          # Primary dataset (260 x 36)
│   └── data_dictionary.md             # Column definitions, units, sources
├── dashboard/
│   └── STI_HIV_Syndemic_Dashboard.html # Self-contained interactive dashboard
├── figures/                            # Publication-quality figures (PNG + SVG)
├── tests/
│   └── test_pipeline.py               # Unit tests for data integrity
├── docs/
│   └── methods_supplement.md          # Extended methods documentation
├── requirements.txt                    # Pinned Python dependencies
├── Dockerfile                          # Reproducible computational environment
├── CITATION.cff                        # Structured citation file
└── .github/workflows/ci.yml           # Automated lint + test on push
```

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts.git
cd sti-hiv-syndemic-ghana-260districts
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or use Docker:

```bash
docker build -t sti-hiv-syndemic .
docker run --rm -v $(pwd):/app sti-hiv-syndemic python src/build_dataset_and_analysis.py
```

### 3. Run the analysis pipeline

```bash
python src/build_dataset_and_analysis.py
```

Outputs: `data/master_260district.csv`, `analysis_results.json`, `gdf.pkl`, `analysis_objects.pkl`

### 4. Generate figures

```bash
python src/generate_figures.py
```

Outputs 5 publication-quality figures to `figures/` (PNG 300 DPI + SVG vector).

### 5. Open the interactive dashboard

Open `dashboard/STI_HIV_Syndemic_Dashboard.html` in any modern browser. No server required.

---

## Data Sources

| Source | Variables | Year |
|--------|-----------|------|
| Ghana Demographic and Health Survey (DHS) | HIV prevalence, behavioural indicators | 2014, 2022 |
| Ghana Population and Housing Census | Population denominators, district boundaries | 2021 |
| WHO Global Health Observatory | ANC syphilis seroprevalence | 2022 |
| Ghana Statistical Service (GSS) | District poverty index, literacy rates | 2021 |

> District-level estimates were produced by model-based small-area estimation from regional DHS data using Census 2021 auxiliary covariates. Raw DHS microdata are not redistributed in compliance with DHS access policies.

---

## Methods Summary

1. **Small-area estimation** — Regional DHS estimates disaggregated to 260 health districts using poverty and literacy covariates from Census 2021.
2. **Syndemic Burden Index (SBI)** — Composite `(HIV_norm + STI_norm)/2 x 10` on 0-10 scale.
3. **Spatial autocorrelation** — Global Moran I (Queen contiguity + KNN-5 fallback) for HIV, STI, and SBI.
4. **Bivariate LISA** — Co-clustering of HIV prevalence x STI incidence using esda `Moran_Local_BV`.
5. **K-means clustering** — k=4 optimal by silhouette coefficient; clusters labelled by ascending mean SBI.
6. **XGBoost + SHAP** — Binary high/low syndemic burden classification; leave-one-region-out spatial CV (9 folds); native XGBoost SHAP (`pred_contribs=True`).
7. **Spatial Lag Regression** — OLS with W·STI spatial lag predicting HIV prevalence (statsmodels).

---

## Reporting Guideline

STROBE checklist for ecological observational studies.

---

## Reproducibility

All random seeds set explicitly (`random_state=42`). Run `pytest tests/ -v` to validate pipeline outputs against expected ranges.

---

## Ethical Approval

Ethical review was waived for this study as it relied solely on publicly accessible, de-identified secondary data from the GSS, DHS and WHO, with no individual clinical or patient-level data obtained or analyzed.


---

## Citation

See `CITATION.cff` for structured citation. Plain text:

```
Ghanem VG. STI and HIV syndemic burden: geospatial co-clustering and
behavioural determinants in Ghana. 2026.
```

---

## License

MIT. See [LICENSE](LICENSE).

## Contact

Valentine Golden Ghanem | ORCID: 0009-0002-8332-0220
Ghana COCOBOD Cocoa Clinic, Accra, Ghana
valentineghanem@gmail.com
