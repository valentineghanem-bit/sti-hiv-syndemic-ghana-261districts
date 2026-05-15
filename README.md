# STI and HIV Syndemic Burden — Geospatial Co-clustering and Behavioural Determinants in Ghana

[![CI](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/actions) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0002--8332--0220-green.svg)](https://orcid.org/0009-0002-8332-0220)

**Author:** Valentine Golden Ghanem | Ghana COCOBOD Cocoa Clinic, Accra, Ghana  
**ORCID:** [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)  
**Reporting standard:** STROBE  
**Date:** May 2026

> Ghanem VG. *STI and HIV syndemic burden: geospatial co-clustering and behavioural determinants in Ghana.* 2026. (Submitted.)

---

## Overview

This study quantifies the syndemic co-burden of sexually transmitted infections (STIs) and HIV across Ghana's 260 districts using geospatial co-clustering and machine learning. A Syndemic Burden Index (SBI) was constructed to identify districts where STI and HIV burdens spatially overlap, and XGBoost with SHAP interpretability was used to identify the leading behavioural and structural determinants of co-burden. The analysis integrates Ghana DHS, WHO GHO, and Ghana Statistical Service data to produce district-level syndemic risk maps.

---

## Key Findings

| Metric | Value |
|--------|-------|
| HIV Global Moran's I | 0.768 (p < 0.001) |
| STI Global Moran's I | 0.514 (p < 0.001) |
| Bivariate LISA (HIV × STI) Moran's I | 0.497 (p = 0.001) |
| Bivariate High-High hotspot districts | 35 |
| Syndemic Overlap Index | 0.331 (86/260 districts) |
| XGBoost Spatial CV AUC | 0.972 ± 0.031 |
| Spatial Lag Regression R² | 0.684 |
| Optimal K-means clusters | 4 (silhouette = 0.234) |

---

## Repository Structure

```
sti-hiv-syndemic-ghana-260districts/
├── src/
│   ├── build_dataset_and_analysis.py
│   └── generate_figures.py
├── data/
│   ├── master_260district.csv
│   └── data_dictionary.md
├── dashboard/
│   └── STI_HIV_Syndemic_Dashboard.html
├── figures/
├── tests/
├── docs/
│   └── methods_supplement.md
├── requirements.txt
├── Dockerfile
└── CITATION.cff
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

### 3. Run the pipeline

```bash
python src/build_dataset_and_analysis.py
python src/generate_figures.py
```

### 4. Run tests

```bash
pytest tests/ -v
```

### 5. Open the interactive dashboard

Open `dashboard/STI_HIV_Syndemic_Dashboard.html` in any modern browser. No server required.

---

## Data Sources

| Source | Variables | Year | Access |
|--------|-----------|------|--------|
| Ghana DHS | HIV prevalence, behavioural indicators | 2014 / 2022 | dhsprogram.com (registration) |
| Ghana Census | District socioeconomic indicators | 2021 | Ghana Statistical Service |
| WHO Global Health Observatory | ANC syphilis screening rates | 2022 | who.int/data/gho (open) |
| Ghana Statistical Service | District administrative boundaries | 2021 | statsghana.gov.gh |

---

## Methods Summary

| Method | Tool | Purpose |
|--------|------|---------|
| Small-area estimation | Custom | District-level STI/HIV burden interpolation |
| Syndemic Burden Index (SBI) | Custom | Composite co-burden scoring |
| Global Moran's I | esda / libpysal | Spatial autocorrelation (HIV, STI separately) |
| Bivariate LISA | esda | HIV × STI co-clustering |
| K-means (k=4) | scikit-learn | District risk typology |
| XGBoost + SHAP | xgboost / shap | Risk prediction and driver identification |
| Spatial Lag Regression | spreg | Spatially-adjusted association modelling |

---

## Reproducibility

- Random seed: 42 throughout  
- Reporting: STROBE  
- All random seeds set explicitly (`random_state=42`)  
- Spatial CV used throughout to prevent spatial leakage

---

## Ethical Statement

Ethical review was waived. This study used exclusively publicly accessible, de-identified secondary data. No individual patient-level data were used and no primary data collection from human participants was conducted.

---

## Citation

```bibtex
@misc{ghanem2026stihiv,
  author = {Ghanem, Valentine Golden},
  title  = {STI and HIV Syndemic Burden --- Geospatial Co-clustering and Behavioural Determinants in Ghana},
  year   = {2026},
  url    = {https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts}
}
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Contact

Valentine Golden Ghanem  
Ghana COCOBOD Cocoa Clinic, Accra, Ghana  
valentineghanem@gmail.com  
ORCID: [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)
