"""
Unit tests for STI-HIV Syndemic Ghana pipeline.
Uses master_260district.csv as the validation target.
Run: pytest tests/ -v
"""
import os, pytest
import pandas as pd
import numpy as np

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "master_260district.csv")

@pytest.fixture(scope="module")
def df():
    return pd.read_csv(DATA_PATH)

def test_row_count(df):
    """Dataset must have exactly 260 districts."""
    assert len(df) == 260, f"Expected 260 rows, got {len(df)}"

def test_required_columns(df):
    required = [
        "district", "region", "hiv_prevalence_pct", "sti_incidence_pct",
        "syndemic_burden_index", "higher_risk_sex_w_pct", "condom_use_w_pct",
        "vct_knowledge_pct", "lisa_bv_q", "cluster_label", "high_syndemic"
    ]
    missing = [c for c in required if c not in df.columns]
    assert not missing, f"Missing columns: {missing}"

def test_hiv_range(df):
    """HIV prevalence must be in plausible range (0-30%)."""
    assert df["hiv_prevalence_pct"].between(0, 30).all()

def test_sti_range(df):
    """STI incidence must be in plausible range (0-10%)."""
    assert df["sti_incidence_pct"].between(0, 10).all()

def test_sbi_range(df):
    """Syndemic Burden Index must be on [0, 10] scale."""
    assert df["syndemic_burden_index"].between(0, 10).all()

def test_no_missing_key_vars(df):
    """Core analytical variables must have no missing values."""
    key_vars = ["hiv_prevalence_pct", "sti_incidence_pct", "syndemic_burden_index"]
    for v in key_vars:
        n_missing = df[v].isna().sum()
        assert n_missing == 0, f"{v} has {n_missing} missing values"

def test_high_syndemic_binary(df):
    """high_syndemic must be binary (0 or 1)."""
    vals = set(int(v) for v in df["high_syndemic"].unique())
    assert vals <= {0, 1}, f"high_syndemic has non-binary values: {vals}"

def test_cluster_labels(df):
    """Cluster labels must be exactly 4 distinct values."""
    n_clusters = df["cluster_label"].nunique()
    assert n_clusters == 4, f"Expected 4 clusters, got {n_clusters}"

def test_lisa_bv_quadrants(df):
    """lisa_bv_q uses integer codes 1=HH, 2=LH, 3=LL, 4=HL (esda encoding).
    Significant HH districts must equal 35 (canonical value)."""
    actual_q = set(int(v) for v in df["lisa_bv_q"].unique())
    valid_q = {1, 2, 3, 4}
    unexpected = actual_q - valid_q
    assert not unexpected, f"Unexpected LISA quadrant codes: {unexpected}"
    sig_hh = int(((df["lisa_bv_q"] == 1) & (df["lisa_bv_sig"] == 1)).sum())
    assert sig_hh == 35, f"Expected 35 significant HH districts, got {sig_hh}"

def test_population_positive(df):
    """Total population must be positive where available.
    Note: 25 districts lack Census 2021 population data (NaN is acceptable)."""
    pop_valid = df["total_pop"].dropna()
    assert (pop_valid > 0).all(), "Some districts have zero or negative population"
    n_missing = df["total_pop"].isna().sum()
    assert n_missing <= 30, f"Excessive missing population data: {n_missing} districts"

def test_district_uniqueness(df):
    """District names must be unique."""
    dupes = df["district"].duplicated().sum()
    assert dupes == 0, f"{dupes} duplicate district names found"

def test_condom_pct_range(df):
    """Condom use percentage must be 0-100."""
    assert df["condom_use_w_pct"].between(0, 100).all()
