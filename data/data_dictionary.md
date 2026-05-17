# Data Dictionary — master_261district.csv

| Column | Type | Unit | Description | Source |
|--------|------|------|-------------|--------|
| district | str | — | District name (uppercase, stripped) | GeoJSON |
| region | str | — | Administrative region (16 current) | GeoJSON |
| lat | float | decimal degrees | District centroid latitude | Census 2021 |
| lon | float | decimal degrees | District centroid longitude | Census 2021 |
| total_pop | int | persons | Total district population | Ghana Census 2021 |
| hiv_prevalence_pct | float | % | HIV prevalence (biomarker-confirmed, model-based SAE) | Ghana DHS 2014 |
| sti_incidence_pct | float | % | STI incidence proxy (WHO ANC syphilis × behavioural multiplier) | WHO GHO 2022 |
| syndemic_burden_index | float | 0–10 | (HIV_norm + STI_norm)/2 × 10 | Derived |
| higher_risk_sex_w_pct | float | % | Women reporting higher-risk sexual partner | Ghana DHS 2022 |
| condom_use_w_pct | float | % | Women using condom at last higher-risk sex | Ghana DHS 2022 |
| vct_knowledge_pct | float | % | MTCT drug prevention knowledge (VCT proxy) | Ghana DHS 2022 |
| condom_negotiation_pct | float | % | Women justified in asking condom use (stigma/empowerment proxy) | Ghana DHS 2022 |
| poverty_rate | float | % | Incidence of poverty | Ghana Census 2021 |
| literacy_rate_census | float | % | District literacy rate (derived from illiterate_pop/total_pop) | Ghana Census 2021 |
| medical_density | float | per 1,000 | Healthcare workers per 1,000 population | GHS DHIMS2 2022 |
| lisa_bv_q | int | 1–4 | Bivariate LISA quadrant (1=HH,2=LH,3=LL,4=HL) | Derived (esda) |
| lisa_bv_sig | int | 0/1 | Bivariate LISA significance (pseudo-p<0.05) | Derived (esda) |
| cluster_label | str | — | K-means cluster label (k=4) | Derived |
| high_syndemic | int | 0/1 | SBI > 75th percentile (threshold=5.53) | Derived |
