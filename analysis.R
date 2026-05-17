# analysis.R — STI–HIV Syndemic Ghana 260 Districts
# Spatial regression (SLM/SEM) + spatial lag diagnostics
# Author: Valentine Golden Ghanem | ORCID: 0009-0002-8332-0220
# Usage: Rscript analysis.R
suppressPackageStartupMessages({
  library(spdep)
  library(spatialreg)
  library(ggplot2)
  library(dplyr)
  library(readr)
})
set.seed(42)

cat("── Loading data ──────────────────────────────────────────────────────\n")
df <- read_csv("data/master_261district.csv", show_col_types = FALSE)
df <- df |> filter(!is.na(lat) & !is.na(lon))
cat(sprintf("Loaded: %d districts × %d variables\n", nrow(df), ncol(df)))

# ── 1. Spatial weights (Queen contiguity approximated via KNN-5) ──────────────
coords <- cbind(df$lon, df$lat)
knn5   <- knearneigh(coords, k = 5)
W      <- nb2listw(knn2nb(knn5), style = "W")

# ── 2. Moran's I for HIV, STI, SBI ───────────────────────────────────────────
cat("\n── Global Moran's I ──────────────────────────────────────────────────\n")
for (var in c("hiv_prevalence_pct", "sti_incidence_pct", "syndemic_burden_index")) {
  if (var %in% names(df)) {
    mi <- moran.test(df[[var]], W, randomisation = TRUE)
    cat(sprintf("  %-28s  I=%.4f  z=%.3f  p=%.4f\n",
                var, mi$estimate[1], mi$statistic, mi$p.value))
  }
}

# ── 3. Spatial Lag Regression: HIV ~ STI + behavioural predictors ─────────────
cat("\n── Spatial Lag Model: HIV prevalence ─────────────────────────────────\n")
predictors <- intersect(c("sti_incidence_pct", "condom_use_m_pct", "vct_knowledge_pct",
                           "poverty_rate", "literacy_rate_census",
                           "higher_risk_sex_w_pct"), names(df))
fml <- as.formula(paste("hiv_prevalence_pct ~", paste(predictors, collapse = " + ")))
ols <- lm(fml, data = df)
slm <- lagsarlm(fml, data = df, listw = W)
sem <- errorsarlm(fml, data = df, listw = W)
cat(sprintf("  OLS AIC=%.2f  |  SLM rho=%.4f AIC=%.2f  |  SEM lambda=%.4f AIC=%.2f\n",
            AIC(ols), slm$rho, AIC(slm), sem$lambda, AIC(sem)))
print(coef(summary(slm)))

# ── 4. Bivariate Moran's I (HIV × STI) — via permutation ──────────────────────
cat("\n── Bivariate spatial lag (HIV lagged STI) ────────────────────────────\n")
if (all(c("hiv_prevalence_pct", "sti_incidence_pct") %in% names(df))) {
  sti_lag <- lag.listw(W, df$sti_incidence_pct)
  bv_lm   <- lm(hiv_prevalence_pct ~ sti_lag, data = df)
  cat(sprintf("  Bivariate Moran slope = %.4f  R2 = %.4f\n",
              coef(bv_lm)[2], summary(bv_lm)$r.squared))
}

# ── 5. Spatial Error Model: SBI ───────────────────────────────────────────────
cat("\n── Spatial Error Model: Syndemic Burden Index ────────────────────────\n")
if ("syndemic_burden_index" %in% names(df)) {
  fml2 <- as.formula(paste("syndemic_burden_index ~",
                            paste(predictors, collapse = " + ")))
  sem2 <- errorsarlm(fml2, data = df, listw = W)
  cat(sprintf("  lambda = %.4f  AIC = %.2f\n", sem2$lambda, AIC(sem2)))
  print(coef(summary(sem2)))
}
cat("\nAnalysis complete.\n")
