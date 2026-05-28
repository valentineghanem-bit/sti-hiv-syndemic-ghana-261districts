# STI and HIV Syndemic Burden — Geospatial Co-clustering and Behavioural Determinants in Ghana

[![CI](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts/actions) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/) [![R 4.3+](https://img.shields.io/badge/R-4.3+-blue.svg)](https://www.r-project.org/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0002--8332--0220-green.svg)](https://orcid.org/0009-0002-8332-0220)

**Author:** Valentine Golden Ghanem | Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**ORCID:** [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)
**Affiliation:** Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**Reporting standard:** STROBE
**Date:** May 2026
**Status:** Manuscript in preparation

---

## 1. Abstract

This study quantifies the syndemic co-burden of sexually transmitted infections (STIs) and HIV across Ghana's 261 districts using geospatial co-clustering and machine learning. A **Syndemic Burden Index (SBI)** was constructed to identify districts where STI and HIV burdens spatially overlap. XGBoost with SHAP interpretability identifies the leading behavioural and structural determinants of co-burden. Bivariate LISA reveals strong spatial co-clustering (Moran's I = 0.564), with 54 confirmed High-High co-burden districts. The analysis integrates Ghana DHS, WHO GHO, and Ghana Statistical Service data to produce district-level syndemic risk maps for programmatic targeting.

---

## 2. Research Question & Aims

- **Primary:** Quantify spatial co-clustering of STI and HIV burden across Ghana's 261 districts.
- **Secondary:** (a) Construct and validate the Syndemic Burden Index (SBI); (b) identify behavioural and structural determinants using XGBoost + SHAP; (c) typologise districts via K-means clustering; (d) estimate spatial-lag regression to quantify associations corrected for spatial dependence.

---

## 3. Methods Summary

| Method | Tool | Purpose |
|--------|------|---------|
| Small-area estimation | Custom | District-level STI/HIV burden interpolation |
| Syndemic Burden Index (SBI) | Custom | Composite co-burden scoring |
| Global Moran's I | esda / libpysal | Spatial autocorrelation (HIV, STI separately) |
| Bivariate LISA | esda | HIV × STI co-clustering |
| K-means (k=4) | scikit-learn | District risk typology |
| XGBoost + SHAP | xgboost / shap | Risk prediction and driver identification |
| Spatial Lag Regression | spreg | Spatially-adjusted association modelling |
| Spatial diagnostics | spdep / spatialreg (R) | OLS / SLM / SEM model selection |

---

## 4. Data Sources

| Source | Variables | Year | Access |
|--------|-----------|------|--------|
| Ghana DHS | HIV prevalence, behavioural indicators | 2014 / 2022 | [dhsprogram.com](https://dhsprogram.com) (registration) |
| Ghana Census 2021 | District socioeconomic indicators | 2021 | [statsghana.gov.gh](https://statsghana.gov.gh) |
| WHO Global Health Observatory | ANC syphilis screening rates | 2022 | [who.int/data/gho](https://www.who.int/data/gho) (open) |
| Ghana Statistical Service | District administrative boundaries | 2021 | [statsghana.gov.gh](https://statsghana.gov.gh) |

> DHS data accessed under signed Data Use Agreement (ICF International). No individual participant data redistributed.

---

## 5. Key Findings

| Metric | Value |
|--------|-------|
| HIV Global Moran's I | 0.838 (p < 0.001) |
| STI Global Moran's I | 0.534 (p < 0.001) |
| Bivariate LISA (HIV × STI) Moran's I | 0.564 (p < 0.001) |
| Bivariate High-High hotspot districts | 54 |
| Syndemic overlap (SBI > threshold) | 101 / 261 districts (38.7%) |
| XGBoost 5-fold CV AUC | 0.911 |
| Districts analysed | 261 (Guan District added 2026-05) |

---

## 6. Repository Structure

```
sti-hiv-syndemic-ghana-261districts/
├── src/
│   ├── build_dataset_and_analysis.py  # Full pipeline
│   └── generate_figures.py            # 300 DPI publication figures
├── scripts/
│   ├── spatial_utils.py               # Reusable spatial analysis utilities
│   └── spatial_diagnostics.R          # R: spatial autocorrelation diagnostics
├── app.py                             # Plotly Dash interactive application
├── analysis.R                         # R: spatial regression + SBI diagnostics
├── data/
│   ├── master_261district.csv
│   └── data_dictionary.md
├── dashboard/
│   └── STI_HIV_Syndemic_Dashboard.html
├── poster/
│   └── STI_HIV_Syndemic_Poster.html
├── figures/                           # Publication figures (PNG + SVG)
├── tests/
│   └── test_pipeline.py
├── docs/
│   └── methods_supplement.md
├── requirements.txt
├── Dockerfile
└── CITATION.cff
```

---

## 7. Reproducibility

### 7.1 Requirements

- Python 3.12 (pinned in `requirements.txt`)
- R 4.3+ with packages: spdep, spatialreg, dplyr (see `analysis.R` header)
- Random seed: 42 throughout
- Estimated runtime: ~8–12 minutes on a standard laptop
- Tested on: Ubuntu 22.04 / macOS 14 / Windows 11 (CI: GitHub Actions)

### 7.2 Clone & install

```bash
git clone https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts.git
cd sti-hiv-syndemic-ghana-261districts
pip install -r requirements.txt
```

### 7.3 Run the analytical pipeline

```bash
python src/build_dataset_and_analysis.py
python src/generate_figures.py
```

### 7.4 Run the test suite

```bash
pytest tests/ -v
```

### 7.5 Launch the interactive Dash application

```bash
python app.py
# Visit http://127.0.0.1:8050
```

### 7.6 Open the static HTML dashboard

```bash
# macOS
open dashboard/STI_HIV_Syndemic_Dashboard.html
# Windows
start dashboard/STI_HIV_Syndemic_Dashboard.html
# Linux
xdg-open dashboard/STI_HIV_Syndemic_Dashboard.html
```

---

## 8. Outputs

| Output | Description |
|--------|-------------|
| `data/` | Master CSV, SBI scores, LISA results, SHAP values |
| `figures/` | Publication-quality PNG and SVG figures |
| `dashboard/` | Self-contained interactive HTML dashboard |
| `poster/` | A0 conference poster (HTML, print-ready) |

## 8a. Downloadable Artefacts (HTML)

Both the interactive dashboard and the conference poster are committed as self-contained HTML files — no server, no build step required.

| Artefact | View on GitHub | Live preview | Direct download (raw HTML) |
|----------|---------------|--------------|---------------------------|
| Interactive dashboard | [View](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts/blob/main/dashboard/STI_HIV_Syndemic_Dashboard.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts/blob/main/dashboard/STI_HIV_Syndemic_Dashboard.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts/main/dashboard/STI_HIV_Syndemic_Dashboard.html) |
| Conference poster | [View](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts/blob/main/poster/STI_HIV_Syndemic_Poster.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts/blob/main/poster/STI_HIV_Syndemic_Poster.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts/main/poster/STI_HIV_Syndemic_Poster.html) |

> **Tip:** The dashboard works fully offline once downloaded. The poster is print-ready at A0 (841 × 1189 mm).

---

## 9. Reporting Standard

This study follows the **STROBE** (Strengthening the Reporting of Observational Studies in Epidemiology) reporting guideline for observational ecological studies.

---

## 10. Ethical Statement

This study analyses publicly released aggregate data from the Ghana Demographic and Health Survey (ICF International), the WHO Global Health Observatory, and the Ghana Statistical Service 2021 Census. No individual participant data were accessed. All inputs are de-identified district and regional summary statistics. Ethical review was not required for analysis of publicly available aggregate statistics; DHS data were accessed under the standard DHS Programme Data Use Agreement.

---

## 11. Citation

**APA:**
Ghanem, V. G. (2026). *STI and HIV Syndemic Burden — Geospatial Co-clustering and Behavioural Determinants in Ghana.* GitHub. https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts

**BibTeX:**
```bibtex
@misc{ghanem2026stihiv,
  author = {Ghanem, Valentine Golden},
  title  = {STI and HIV Syndemic Burden --- Geospatial Co-clustering and Behavioural Determinants in Ghana},
  year   = {2026},
  url    = {https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-261districts}
}
```

A machine-readable citation is provided in `CITATION.cff`.

---

## 12. License

Code is released under the **MIT License** — see [LICENSE](LICENSE) for details.
Outputs and figures: **CC BY 4.0**.

---

## 13. Author & Contact

**Valentine Golden Ghanem**
Ghana COCOBOD Cocoa Clinic, Accra, Ghana
Email: valentineghanem@gmail.com
ORCID: [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)

---

## 14. Acknowledgements

The author thanks the DHS Programme and ICF International for the Ghana DHS data, the WHO for Global Health Observatory indicators, and the Ghana Statistical Service for Census district files and boundary geometries. Spatial analysis relied on esda, libpysal, spreg, spdep, and spatialreg. Ensemble modelling used XGBoost and scikit-learn; interpretability used SHAP. The syndemic framework draws on Singer's foundational work on co-occurring epidemics.
