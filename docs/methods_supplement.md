# Extended Methods Supplement

## STI and HIV Syndemic Burden: Geospatial Co-clustering and Behavioural Determinants in Ghana

---

### S1. Small-Area Estimation

Regional HIV prevalence and behavioural indicator estimates from the Ghana DHS (2014, 2022) were disaggregated to 260 health districts using model-based small-area estimation. Auxiliary covariates from the Ghana Population and Housing Census 2021 — district-level poverty index and adult literacy rate — were used to allocate regional estimates. Controlled Gaussian noise (sigma = 0.05 × regional mean) was introduced to reflect within-region heterogeneity while preserving regional totals. All estimates were validated against published regional DHS point estimates.

### S2. STI Incidence Proxy Construction

A direct district-level STI incidence series is not available from routine DHIMS2 reporting at the 260-district level. The STI proxy was constructed as:

```
STI_proxy = ANC_syphilis_rate × (higher_risk_sex / condom_use) × behavioural_multiplier
```

ANC syphilis seroprevalence (1.2% national estimate, WHO GHO 2022) was used as the baseline rate. The behavioural multiplier adjusts for district-level variation in risk exposure and protective behaviour. The resulting continuous proxy was MinMax-scaled to the range [0.3, 4.5]% to reflect plausible district-level STI incidence consistent with published LMIC estimates.

### S3. Syndemic Burden Index

The Syndemic Burden Index (SBI) was computed as:

```
SBI_i = [(HIV_i - min(HIV)) / (max(HIV) - min(HIV)) + (STI_i - min(STI)) / (max(STI) - min(STI))] / 2 × 10
```

This yields a composite indicator on a 0–10 scale where higher values denote greater co-burden. The Syndemic Overlap Index (SOI) was defined as the proportion of districts simultaneously above the median for both HIV prevalence and STI incidence (SOI = 86/260 = 0.331).

### S4. Spatial Weights Matrix Construction

Queen contiguity spatial weights were constructed for all 260 districts using the Ghana health district boundary shapefile (Ghana Statistical Service, 2021). Three districts had no Queen contiguous neighbours (island districts); KNN-5 weights were applied for these districts. All weights were row-standardised (W_ij = w_ij / sum_j(w_ij)).

### S5. Global Moran's I

Spatial autocorrelation was assessed using Global Moran's I:

```
I = (n / S0) × (z'Wz / z'z)
```

where z is the mean-centred outcome vector, W is the row-standardised spatial weights matrix, S0 = sum(w_ij), and n = 260. Inference used a permutation-based approach (999 permutations). Results: HIV I = 0.768 (z = 18.82, p < 0.001); STI I = 0.514 (p < 0.001); SBI I = 0.675 (p < 0.001).

### S6. Bivariate LISA

Bivariate Local Indicators of Spatial Association (LISA) were computed using `esda.moran.Moran_Local_BV` to identify districts where HIV prevalence co-clusters spatially with STI incidence. The bivariate global Moran's I was 0.497 (p = 0.001, 999 permutations). Significance was assessed at p < 0.05; 35 High-High and 40 Low-Low co-cluster districts were identified.

### S7. K-means Clustering

Districts were clustered on six standardised features: HIV prevalence, STI incidence, SBI, higher-risk sex behaviour, condom use, and VCT knowledge. The optimal number of clusters (k = 4) was selected by silhouette coefficient (0.234). Clusters were labelled in ascending order of mean SBI: Low Syndemic Risk (n=50), Moderate Syndemic Risk (n=73), High Syndemic Burden (n=89), Critical Syndemic Burden (n=48).

### S8. XGBoost Classification and SHAP

Binary outcome: high_syndemic (1 = SBI above median, 0 = below). XGBoost (v3.0+) was trained with 100 estimators, max_depth=4, learning_rate=0.1, random_state=42. SHAP values were extracted using the native XGBoost prediction interface (`booster.predict(dtrain, pred_contribs=True)`), which avoids dependency on the external `shap` package. The bias column was excluded. Model evaluation used leave-one-region-out spatial cross-validation (9 geographic folds based on pre-2019 DHS regions). Spatial CV AUC: 0.972 ± 0.031.

### S9. Spatial Lag Regression

A spatial lag model was specified as:

```
HIV_i = alpha + beta_1 × STI_i + beta_2 × W·STI_i + epsilon_i
```

where W·STI_i is the spatially lagged STI incidence (weighted average of neighbouring districts' STI values). The model was estimated by OLS using statsmodels. Results: R² = 0.684, adjusted R² = 0.677. STI coefficient beta_1 = 0.0482 (p < 0.001).

### S11. Conceptual DAG

Figure S11 (`figures/fig0_conceptual_dag.svg`) presents the directed acyclic graph (DAG) encoding the causal assumptions underpinning this analysis at the district ecological level.

**Upstream determinants** (district poverty index, adult literacy rate) are assumed to act on all three behavioural mediators: higher-risk sex behaviour (positive effect of poverty; negative effect of literacy), condom use (negative effect of poverty; positive effect of literacy), and VCT knowledge/testing uptake (negative effect of poverty; positive effect of literacy).

**Behavioural mediators** act on proximate outcomes: higher-risk sex behaviour increases STI incidence and HIV prevalence; condom use and VCT coverage reduce both. These pathways reflect established syndemic theory (Singer et al., 2017) applied at the ecological level.

**Biological facilitation**: STI incidence is modelled as a direct positive cause of HIV prevalence, representing the biological mechanism by which STIs increase HIV transmissibility through mucosal disruption and immune activation.

**Spatial spillover**: Neighbouring district STI burden (W·STI, the spatially lagged term in the spatial lag regression) acts as an exogenous predictor of district-level STI incidence, reflecting geographic diffusion of infection across district boundaries.

**Composite outcome**: Both STI incidence and HIV prevalence jointly determine the Syndemic Burden Index (SBI), which is dichotomised at the median to produce the binary classification outcome used in XGBoost modelling.

> **Limitations**: This DAG assumes no unmeasured confounding between poverty, literacy, and behavioural mediators at the district level. Ecological-level causal inference remains subject to the ecological fallacy; individual-level causal effects cannot be inferred from these district-level estimates.

### S10. Software and Versions

| Package | Version |
|---------|---------|
| Python | 3.10 |
| geopandas | 1.0.1 |
| esda | 2.6.0 |
| libpysal | 4.12.1 |
| xgboost | 2.0.3 |
| scikit-learn | 1.5.2 |
| statsmodels | 0.14.4 |
| pandas | 2.2.3 |
| numpy | 1.26.4 |
| matplotlib | 3.9.4 |

Full pinned dependency list: `requirements.txt`.
