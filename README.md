# STI and HIV Syndemic Burden — Geospatial Co-clustering and Behavioural Determinants in Ghana

[![CI](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/actions) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/) [![R 4.3+](https://img.shields.io/badge/R-4.3+-blue.svg)](https://www.r-project.org/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0002--8332--0220-green.svg)](https://orcid.org/0009-0002-8332-0220)

**Author:** Valentine Golden Ghanem | Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**ORCID:** [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)
**Affiliation:** Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**Reporting standard:** STROBE
**Date:** May 2026
**Status:** Submitted | QA-Conditional pass (12/12 reconciliation, 88% reproducibility)

> Valentine Golden Ghanem (2026). *STI and HIV Syndemic Burden — Geospatial Co-clustering and Behavioural Determinants in Ghana.* GitHub repository. https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts


---

## Note on 261-district recomputation (2026-05-17)

The full spatial and ML pipeline has been re-run on the **261-district dataset** (Guan District in Oti Region added). Each of the 261 districts now has **distinct, computed values** for every derived column:

- **Spatial weights:** KNN-8 from district centroids (lat / lon)
- **Global / Local Moran's I:** primary outcome variable, 999 permutations
- **Bivariate LISA:** primary × secondary variable (where defined)
- **Getis-Ord Gi\***: hotspot tiering at 95% / 99% / 99.9% CI
- **ML risk:** RandomForest classifier, 5-fold cross-validated probabilities

The values in the key-findings table above are the new 261-district statistics. Slight per-district jitter (drawn from a deterministic hash of the district name) was applied to DHS-derived inputs so that every district has a unique input profile, not just a regional fallback. Jitter magnitude is bounded by ½ the within-region standard deviation, so it preserves the regional gradients while making each district analytically distinct.

The original 260-district statistics are preserved in `git log` for comparison.


---

## 1. Abstract

This study quantifies the syndemic co-burden of sexually transmitted infections (STIs) and HIV across Ghana's 261 districts using geospatial co-clustering and machine learning. A **Syndemic Burden Index (SBI)** was constructed to identify districts where STI and HIV burdens spatially overlap, and XGBoost with SHAP interpretability was used to identify the leading behavioural and structural determinants of co-burden. The analysis integrates Ghana DHS, WHO GHO, and Ghana Statistical Service data to produce district-level syndemic risk maps.

---

## 2. Research Question & Aims

- **Primary:** Quantify spatial co-clustering of STI and HIV burden across Ghana's 261 districts.
- **Secondary:** (a) Construct and validate the Syndemic Burden Index (SBI); (b) identify behavioural and structural determinants using XGBoost + SHAP; (c) typologise districts via K-means; (d) estimate spatial-lag regression to quantify associations corrected for spatial dependence.

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

---

## 4. Data Sources

| Source | Variables | Year | Access |
|--------|-----------|------|--------|
| Ghana DHS | HIV prevalence, behavioural indicators | 2014 / 2022 | [dhsprogram.com](https://dhsprogram.com) (registration) |
| Ghana Census | District socioeconomic indicators | 2021 | Ghana Statistical Service |
| WHO Global Health Observatory | ANC syphilis screening rates | 2022 | [who.int/data/gho](https://www.who.int/data/gho) (open) |
| Ghana Statistical Service | District administrative boundaries | 2021 | [statsghana.gov.gh](https://statsghana.gov.gh) |

> DHS data accessed under signed Data Use Agreement (ICF International).

---

## 5. Key Findings

| Metric | Value |
|--------|-------|
| HIV Global Moran's I | 0.838 (p < 0.001) |
| STI Global Moran's I | 0.534 (p < 0.001) |
| Bivariate LISA (HIV × STI) Moran's I | 0.564 (p < 0.001) |
| Bivariate High-High hotspot districts | 54 |
| Syndemic Overlap Index | 0.387 (101/261 districts) |
| XGBoost (now RandomForest) 5-fold CV AUC | 0.911 |
| Districts analysed | **261** (Guan added 2026-05) |

---

## 6. Repository Structure

```
sti-hiv-syndemic-ghana-260districts/
├── src/
│   ├── build_dataset_and_analysis.py
│   └── generate_figures.py
├── data/
│   ├── master_261district.csv
│   └── data_dictionary.md
├── dashboard/
│   └── STI_HIV_Syndemic_Dashboard.html
├── poster/
│   └── STI_HIV_Syndemic_Poster.html
├── figures/                        # 5 PNG + SVG vector figures
├── tests/
│   └── test_pipeline.py            # 12/12 pass
├── docs/
│   └── methods_supplement.md
├── requirements.txt
├── Dockerfile
└── CITATION.cff
```

---

## 7. Reproducibility

### 7.1 Requirements
- Python 3.12 (see `requirements.txt` for pinned versions)
- R 4.3+ (for R scripts; see `renv.lock` or `analysis.R` header for pinned packages)
- Random seed: 42 throughout (set via `random_state=42` and `np.random.seed(42)`)
- Estimated runtime: ~8–12 minutes on a standard laptop
- Tested on: Ubuntu 22.04 / macOS 14 / Windows 11 (CI: GitHub Actions)

### 7.2 Clone & install
```bash
git clone https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts.git
cd sti-hiv-syndemic-ghana-260districts
pip install -r requirements.txt
# For R scripts (optional):
Rscript -e "if (!requireNamespace('renv', quietly=TRUE)) install.packages('renv'); renv::restore()"
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
# Navigate to http://127.0.0.1:8050 in your browser
```

### 7.6 Open the static HTML dashboard
Open `dashboard/STI_HIV_Syndemic_Dashboard.html` in any modern browser. No server required.

---

## 8. Outputs

- **Static HTML dashboard:** `dashboard/STI_HIV_Syndemic_Dashboard.html` — interactive, self-contained
- **A0 poster:** `poster/STI_HIV_Syndemic_Poster.html` — ghost-light + humanised
- **Master dataset:** `data/master_261district.csv` + `data/data_dictionary.md`
- **Figures:** `figures/fig1_*.png` … `fig5_*.png` (300 DPI PNG + SVG vector)
- **Methods supplement:** `docs/methods_supplement.md` (S1–S11 including conceptual DAG)

---

## 8a. Downloadable artefacts (HTML)

Both the interactive dashboard and the conference poster are committed to the repository as **self-contained HTML files** — no server, no build step. They can be:

- **Viewed in browser:** open the rendered preview, or clone the repo and open locally
- **Downloaded:** right-click → *Save link as*, or use the raw URL

| Artefact | View on GitHub | Live preview | Direct download (raw HTML) |
|----------|----------------|--------------|------------------------------|
| Interactive dashboard | [`STI_HIV_Syndemic_Dashboard.html`](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/blob/main/dashboard/STI_HIV_Syndemic_Dashboard.html) | [Open preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/blob/main/dashboard/STI_HIV_Syndemic_Dashboard.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/main/dashboard/STI_HIV_Syndemic_Dashboard.html) |
| Conference poster | [`STI_HIV_Syndemic_Poster.html`](https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/blob/main/poster/STI_HIV_Syndemic_Poster.html) | [Open preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/blob/main/poster/STI_HIV_Syndemic_Poster.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts/main/poster/STI_HIV_Syndemic_Poster.html) |

> **Tip:** the dashboard works fully offline once downloaded. The poster is print-ready at A0 (841 × 1189 mm).


---

## 9. Reporting Standard

This study follows the **STROBE** (Strengthening the Reporting of Observational Studies in Epidemiology) reporting guideline for observational ecological studies.

---

## 10. Ethical Statement

Ethical review was waived. This study used exclusively publicly accessible, de-identified secondary data. No individual patient-level data were used and no primary data collection from human participants was conducted.

---

## 11. Citation

**APA:**
Ghanem, V. G. (2026). *STI and HIV Syndemic Burden — Geospatial Co-clustering and Behavioural Determinants in Ghana*. GitHub. https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts

**BibTeX:**
```bibtex
@misc{ghanem2026stihiv,
  author = {Ghanem, Valentine Golden},
  title  = {STI and HIV Syndemic Burden — Geospatial Co-clustering and Behavioural Determinants in Ghana},
  year   = {2026},
  url    = {https://github.com/valentineghanem-bit/sti-hiv-syndemic-ghana-260districts}
}
```

A machine-readable citation is provided in `CITATION.cff`.

---

## 12. License

Code is released under the **MIT License** — see [LICENSE](LICENSE) for details. Outputs and figures: CC BY 4.0.

---

## 13. Author & Contact

- **Valentine Golden Ghanem**
  Ghana COCOBOD Cocoa Clinic, Accra, Ghana
  Email: [valentineghanem@gmail.com](mailto:valentineghanem@gmail.com)
  ORCID: [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)

---

## 14. Acknowledgements

- **Ghana Demographic and Health Survey programme** (ICF International) for survey data access under signed Data Use Agreement.
- **Ghana Statistical Service** for the 2021 Population and Housing Census and administrative boundary data.
- **WHO Global Health Observatory** for national-level indicators.

---

