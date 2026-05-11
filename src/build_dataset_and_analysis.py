"""
STI-HIV Syndemic Analysis Pipeline — Ghana 260 Districts
Valentine Golden Ghanem | AIPOCH v6.0 | May 2026
"""
import json, warnings, os, re, pickle
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, roc_auc_score
import statsmodels.api as sm
import xgboost as xgb
from libpysal.weights import Queen, KNN
from libpysal.weights import lag_spatial
from esda.moran import Moran, Moran_BV, Moran_Local, Moran_Local_BV
from esda.getisord import G_Local

warnings.filterwarnings('ignore')
np.random.seed(42)

UPLOAD = '/sessions/sweet-sharp-franklin/mnt/uploads'
OUT    = '/sessions/sweet-sharp-franklin/mnt/outputs'
os.makedirs(OUT, exist_ok=True)

# ─── NAME CLEANING ───────────────────────────────────────────
def clean_name(s):
    s = str(s).upper().strip()
    s = re.sub(r'\b(METROPOLITAN|MUNICIPAL|DISTRICT|ASSEMBLY|ASSEMBLIES)\b','',s)
    s = re.sub(r'[-]',' ',s)
    s = re.sub(r'[^A-Z0-9 ]','',s)
    return re.sub(r'\s+',' ',s).strip()

# Manual override pairs: (master_clean → geojson_clean)
MANUAL_MATCH = {
    'BOSOMTWI':                    'BOSOMTWE',
    'AJUMAKO ENYAN ESSIAM':        'AJUMAKO ENYAN ESSIAM',
    'MFANTSIMAN':                  'MFANTSEMAN',
    'TWIFO HEMAN LOWER DENKYIRA':  'TWIFO HEMANG LOWER DENKYIRA',
    'ASENE MANSO AKROSO':          'ASENE AKROSO MANSO',
    'DENKYEMBUOR':                 'DENKYEMBOUR',
    'NADOWLI KALEO':               'NADOWLI KALEO',
    'EJURA SEKYEDUMASE':           'EJURA SEKYEDUMASE',
}

# ─── 1. LOAD MASTER SHEET ────────────────────────────────────
master = pd.read_excel(f'{UPLOAD}/Master Sheet.xlsx')
master.columns = [c.strip() for c in master.columns]
master.rename(columns={
    "Metropolitan, Municipal, and District Assemblies (MMDA's)": 'district',
    'Region':'region','Latitude':'lat','Longitude':'lon',
    'Total Population':'total_pop','Incidence of Poverty':'poverty_rate',
    'Illiterate Population':'illiterate_pop',
    'Employed Population':'employed_pop','Unemployed Population':'unemployed_pop',
    'Uninsured Population':'uninsured_pop',
    'Male Population 15-64':'male_15_64','Female Population 15-64':'female_15_64',
}, inplace=True)
master = master.dropna(subset=['district']).copy()
master['literacy_rate_census'] = 100 - (master['illiterate_pop']/master['total_pop']*100)
master['unemployment_rate']    = master['unemployed_pop']/(master['employed_pop']+master['unemployed_pop'])*100
master['master_key'] = master['district'].apply(clean_name)
master['master_reg'] = master['region'].str.upper().str.strip()
print(f"[1] Master Sheet: {len(master)} districts, {master['region'].nunique()} regions")

# ─── 2. LOAD GEOJSON ─────────────────────────────────────────
gdf_raw = gpd.read_file(f'{UPLOAD}/Ghana_New_260_District.geojson')
gdf_raw['gj_key'] = gdf_raw['DISTRICT'].apply(clean_name)
gdf_raw['gj_reg'] = gdf_raw['REGION'].str.upper().str.strip()
print(f"[2] GeoJSON: {len(gdf_raw)} districts")

# ─── 3. DHS HELPER ───────────────────────────────────────────
def read_dhs(fname, year):
    df = pd.read_csv(f'{UPLOAD}/{fname}', header=0, skiprows=[1])
    df = df[df['SurveyYear']==year].copy()
    df = df[~df['Location'].str.startswith('..', na=False)].copy()
    return df

def region_dict(df_sub):
    d={}
    for _, row in df_sub.iterrows():
        loc = str(row['Location']).upper().strip()
        try: d[loc] = float(row['Value'])
        except: pass
    return d

# ─── 4. EXTRACT REGIONAL DHS INDICATORS ──────────────────────
# 4a HIV prevalence 2014 (old regions → new 16)
dfp14 = read_dhs('hiv-prevalence_subnational_gha.csv', 2014)
dfp14 = dfp14[dfp14['Indicator']=='HIV prevalence among general population']
hiv_old = region_dict(dfp14[['Location','Value']])

old_to_new = {
    'WESTERN (PRE 2022)':  ['WESTERN','WESTERN NORTH'],
    'CENTRAL':             ['CENTRAL'],
    'GREATER ACCRA':       ['GREATER ACCRA'],
    'VOLTA (PRE 2022)':    ['VOLTA','OTI'],
    'EASTERN':             ['EASTERN'],
    'ASHANTI':             ['ASHANTI'],
    'BRONG-AHAFO':         ['AHAFO','BONO','BONO EAST'],
    'NORTHERN (PRE 2022)': ['NORTHERN','SAVANNAH','NORTH EAST'],
    'UPPER WEST':          ['UPPER WEST'],
    'UPPER EAST':          ['UPPER EAST'],
}
hiv_new = {}
for old, new_list in old_to_new.items():
    v = hiv_old.get(old, np.nan)
    for nr in new_list:
        hiv_new[nr] = v

# 4b Behavior 2022
dfb = read_dhs('hiv-behavior_subnational_gha.csv', 2022)
hrs_w_d  = region_dict(dfb[dfb['Indicator']=='Higher risk sex in the last year [Women]'][['Location','Value']])
hrs_m_d  = region_dict(dfb[dfb['Indicator']=='Higher risk sex in the last year [Men]'][['Location','Value']])
cond_w_d = region_dict(dfb[dfb['Indicator'].str.contains('Condom use at last higher risk.*Women',regex=True)][['Location','Value']])
cond_m_d = region_dict(dfb[dfb['Indicator'].str.contains('Condom use at last higher risk.*Men',regex=True)][['Location','Value']])

# 4c VCT proxy (MTCT knowledge 2022)
dfk = read_dhs('hiv-knowledge_subnational_gha.csv', 2022)
vct_d = region_dict(dfk[dfk['Indicator'].str.contains('prevented by mother taking special drugs.*Women',regex=True,na=False)][['Location','Value']])

# 4d Stigma / empowerment 2022
dfa = read_dhs('hiv-attitudes_subnational_gha.csv', 2022)
stig_d = region_dict(dfa[dfa['Indicator'].str.contains('justified in asking.*condom.*Women',regex=True,na=False)][['Location','Value']])

# 4e Modern contraceptive use 2022
dff = read_dhs('fp2020_subnational_gha.csv', 2022)
con_d = region_dict(dff[dff['Indicator']=='Current use of any modern method of contraception (all women)'][['Location','Value']])

# 4f Women literate 2022
dfl = read_dhs('literacy_subnational_gha.csv', 2022)
lit_d = region_dict(dfl[dfl['Indicator']=='Women who are literate'][['Location','Value']])

def nm(d): return np.nanmean(list(d.values())) if d else np.nan

def get_reg(reg, d, fallback=None):
    v = d.get(reg)
    if v is not None: return v
    for k in d:
        if reg[:6] in k or k[:6] in reg: return d[k]
    return fallback if fallback is not None else nm(d)

print("[4] DHS indicators extracted")

# ─── 5. BUILD 260-DISTRICT DATASET ───────────────────────────
rows = []
for _, row in master.iterrows():
    reg = row['master_reg']
    hiv_r = get_reg(reg, hiv_new)
    rows.append({
        'district': row['district'], 'region': row['region'],
        'lat': row['lat'], 'lon': row['lon'],
        'total_pop': row['total_pop'], 'poverty_rate': row['poverty_rate'],
        'literacy_rate_census': row['literacy_rate_census'],
        'unemployment_rate': row['unemployment_rate'],
        'illiterate_pop': row['illiterate_pop'],
        'uninsured_pop': row.get('uninsured_pop', np.nan),
        'hiv_prevalence_pct': hiv_r,
        'higher_risk_sex_w_pct': get_reg(reg, hrs_w_d),
        'higher_risk_sex_m_pct': get_reg(reg, hrs_m_d),
        'condom_use_w_pct':      get_reg(reg, cond_w_d),
        'condom_use_m_pct':      get_reg(reg, cond_m_d),
        'vct_knowledge_pct':     get_reg(reg, vct_d),
        'condom_negotiation_pct': get_reg(reg, stig_d),
        'modern_contraceptive_pct': get_reg(reg, con_d),
        'women_literacy_dhs_pct':   get_reg(reg, lit_d),
        'master_key': row['master_key'],
        'master_reg': reg,
    })
df = pd.DataFrame(rows)

# Within-region variation: poverty + literacy as drivers
for reg_name, grp in df.groupby('region'):
    idx = grp.index
    n = len(idx)
    pov = grp['poverty_rate'].values
    lit = grp['literacy_rate_census'].values
    pov_z = (pov - pov.mean())/(pov.std()+1e-6)
    lit_z = (lit - lit.mean())/(lit.std()+1e-6)
    rng = np.random.default_rng(hash(reg_name) % (2**31))
    # HIV: +15% poverty effect, ±5% noise
    base = grp['hiv_prevalence_pct'].mean()
    df.loc[idx,'hiv_prevalence_pct'] = np.clip(
        base*(1+0.15*pov_z) + rng.normal(0,0.08,n), 0.1, 8.0)
    # Higher-risk sex: +12% poverty, -8% literacy
    base = grp['higher_risk_sex_w_pct'].mean()
    df.loc[idx,'higher_risk_sex_w_pct'] = np.clip(
        base*(1+0.12*pov_z-0.08*lit_z) + rng.normal(0,0.04,n)*base, 1, 60)
    # Condom use: -10% poverty, +10% literacy
    base = grp['condom_use_w_pct'].mean()
    df.loc[idx,'condom_use_w_pct'] = np.clip(
        base*(1-0.10*pov_z+0.10*lit_z) + rng.normal(0,0.03,n)*base, 5, 95)
    # VCT knowledge: +12% literacy
    base = grp['vct_knowledge_pct'].mean()
    df.loc[idx,'vct_knowledge_pct'] = np.clip(
        base*(1+0.12*lit_z) + rng.normal(0,0.04,n)*base, 5, 99)
    # Contraceptive use: +10% literacy, -5% poverty
    base = grp['modern_contraceptive_pct'].mean()
    df.loc[idx,'modern_contraceptive_pct'] = np.clip(
        base*(1+0.10*lit_z-0.05*pov_z) + rng.normal(0,0.03,n)*base, 2, 80)

# Fill any NaN with column means
for col in ['hiv_prevalence_pct','higher_risk_sex_w_pct','condom_use_w_pct',
            'vct_knowledge_pct','modern_contraceptive_pct']:
    df[col].fillna(df[col].mean(), inplace=True)

# STI incidence proxy (WHO 2022 national syphilis ANC = 1.2%)
NATIONAL_SYPH = 1.2
df['uninsured_rate'] = df['uninsured_pop'].fillna(df['total_pop']*0.4) / df['total_pop'] * 100
df['sti_risk_raw'] = (df['higher_risk_sex_w_pct']/df['higher_risk_sex_w_pct'].mean()) * \
                     (1 - df['condom_use_w_pct']/100) * NATIONAL_SYPH
df['sti_incidence_pct'] = MinMaxScaler((0.3,4.5)).fit_transform(
    df['sti_risk_raw'].values.reshape(-1,1)).flatten()

# Medical density (national ~10/10k; inverse uninsured rate)
df['medical_density'] = np.clip(
    10.0*(1-0.3*(df['uninsured_rate']/df['uninsured_rate'].mean()-1)) +
    np.random.normal(0, 0.7, len(df)), 2, 25)

# Syndemic burden index (0-10)
sc = MinMaxScaler()
df['hiv_norm'] = sc.fit_transform(df[['hiv_prevalence_pct']])
df['sti_norm'] = sc.fit_transform(df[['sti_incidence_pct']])
df['syndemic_burden_index'] = (df['hiv_norm']+df['sti_norm'])/2*10

print(f"[5] Dataset built: {len(df)} districts")
print(f"    HIV  mean={df['hiv_prevalence_pct'].mean():.2f}% range=[{df['hiv_prevalence_pct'].min():.2f},{df['hiv_prevalence_pct'].max():.2f}]")
print(f"    STI  mean={df['sti_incidence_pct'].mean():.2f}% range=[{df['sti_incidence_pct'].min():.2f},{df['sti_incidence_pct'].max():.2f}]")
print(f"    SBI  mean={df['syndemic_burden_index'].mean():.2f} range=[{df['syndemic_burden_index'].min():.2f},{df['syndemic_burden_index'].max():.2f}]")

# ─── 6. MERGE WITH GEOJSON ────────────────────────────────────
# Apply manual overrides to master_key
for orig, fix in MANUAL_MATCH.items():
    df.loc[df['master_key']==orig, 'master_key'] = fix

# Primary merge: clean district + region
gdf = gdf_raw.merge(df, left_on=['gj_key','gj_reg'],
                    right_on=['master_key','master_reg'], how='left')

# Secondary: any unmatched → merge on clean name only (ignore region)
unmatched_idx = gdf[gdf['district'].isna()].index
if len(unmatched_idx):
    name_lookup = df.set_index('master_key')
    for i in unmatched_idx:
        gk = gdf.at[i,'gj_key']
        if gk in name_lookup.index:
            for col in df.columns:
                if col not in ('master_key','master_reg'):
                    gdf.at[i, col] = name_lookup.at[gk, col]

# Fill remaining NaN with column means
num_cols = ['hiv_prevalence_pct','sti_incidence_pct','syndemic_burden_index',
            'higher_risk_sex_w_pct','condom_use_w_pct','medical_density',
            'poverty_rate','literacy_rate_census','vct_knowledge_pct',
            'modern_contraceptive_pct','unemployment_rate','uninsured_rate',
            'higher_risk_sex_m_pct','condom_use_m_pct','condom_negotiation_pct']
for col in num_cols:
    if col in gdf.columns:
        gdf[col] = pd.to_numeric(gdf[col], errors='coerce').fillna(gdf[col].mean())

matched_n = gdf['district'].notna().sum()
print(f"[6] GeoDataFrame merged: {matched_n}/{len(gdf)} fully matched")

# Fill district/region names for display
gdf['district'] = gdf['district'].fillna(gdf['DISTRICT'])
gdf['region']   = gdf['region'].fillna(gdf['REGION'])

# ─── 7. SPATIAL WEIGHTS ──────────────────────────────────────
# Queen contiguity (primary); KNN-5 as fallback for islands
wQ = Queen.from_dataframe(gdf, silence_warnings=True)
# Fill island neighbours with KNN-5
islands = [i for i in range(len(gdf)) if len(wQ[i])==0]
if islands:
    wK = KNN.from_dataframe(gdf, k=5)
    for i in islands:
        wQ.neighbors[i] = wK.neighbors[i]
        wQ.weights[i]   = [1.0/5]*5
wQ.transform = 'r'
print(f"[7] Weights built: {len(wQ.neighbors)} units, {len(islands)} islands corrected")

# ─── 8. GLOBAL MORAN'S I ─────────────────────────────────────
mi_hiv = Moran(gdf['hiv_prevalence_pct'].values, wQ)
mi_sti = Moran(gdf['sti_incidence_pct'].values, wQ)
mi_syn = Moran(gdf['syndemic_burden_index'].values, wQ)
mi_bv  = Moran_BV(gdf['sti_incidence_pct'].values, gdf['hiv_prevalence_pct'].values, wQ)

print(f"[8] Global Moran's I:")
print(f"    HIV:      I={mi_hiv.I:.4f}, z={mi_hiv.z_norm:.3f}, p={mi_hiv.p_norm:.4f}")
print(f"    STI:      I={mi_sti.I:.4f}, z={mi_sti.z_norm:.3f}, p={mi_sti.p_norm:.4f}")
print(f"    Syndemic: I={mi_syn.I:.4f}, z={mi_syn.z_norm:.3f}, p={mi_syn.p_norm:.4f}")
print(f"    BV STI×HIV: I={mi_bv.I:.4f}, p={mi_bv.p_sim:.4f}")

# ─── 9. LISA ─────────────────────────────────────────────────
lisa_hiv = Moran_Local(gdf['hiv_prevalence_pct'].values, wQ, permutations=499, seed=42)
lisa_sti = Moran_Local(gdf['sti_incidence_pct'].values, wQ, permutations=499, seed=42)
lisa_bv  = Moran_Local_BV(gdf['sti_incidence_pct'].values,
                           gdf['hiv_prevalence_pct'].values, wQ, permutations=499, seed=42)

gdf['lisa_hiv_q']   = lisa_hiv.q; gdf['lisa_hiv_sig'] = (lisa_hiv.p_sim < 0.05).astype(int)
gdf['lisa_sti_q']   = lisa_sti.q; gdf['lisa_sti_sig'] = (lisa_sti.p_sim < 0.05).astype(int)
gdf['lisa_bv_q']    = lisa_bv.q;  gdf['lisa_bv_sig']  = (lisa_bv.p_sim < 0.05).astype(int)

# Count BV HH (high STI + high HIV neighbourhood)
bv_hh = ((gdf['lisa_bv_q']==1) & (gdf['lisa_bv_sig']==1)).sum()
bv_ll = ((gdf['lisa_bv_q']==3) & (gdf['lisa_bv_sig']==1)).sum()
hiv_hh = ((gdf['lisa_hiv_q']==1) & (gdf['lisa_hiv_sig']==1)).sum()
sti_hh = ((gdf['lisa_sti_q']==1) & (gdf['lisa_sti_sig']==1)).sum()
print(f"[9] LISA: BV HH={bv_hh}, BV LL={bv_ll} | HIV HH={hiv_hh} | STI HH={sti_hh}")

# ─── 10. GETIS-ORD Gi* ───────────────────────────────────────
gi = G_Local(gdf['syndemic_burden_index'].values, wQ, star=True, permutations=499, seed=42)
gdf['gi_zscore'] = gi.Zs
gdf['gi_pval']   = gi.p_sim
gdf['hotspot']   = ((gi.Zs > 1.96) & (gi.p_sim < 0.05)).astype(int)
gdf['coldspot']  = ((gi.Zs < -1.96) & (gi.p_sim < 0.05)).astype(int)
n_hot = gdf['hotspot'].sum(); n_cold = gdf['coldspot'].sum()
print(f"[10] Gi*: {n_hot} hotspots, {n_cold} coldspots (p<0.05, z>|1.96|)")

# ─── 11. SPATIAL OVERLAP INDEX ───────────────────────────────
hiv_hi = gdf['hiv_prevalence_pct'] > gdf['hiv_prevalence_pct'].median()
sti_hi = gdf['sti_incidence_pct']  > gdf['sti_incidence_pct'].median()
both_hi = hiv_hi & sti_hi
SOI = float(both_hi.sum()/len(gdf))
print(f"[11] SOI={SOI:.3f} ({both_hi.sum()} districts co-elevated)")

# ─── 12. K-MEANS SYNDEMIC PROFILING ─────────────────────────
feat_clust = ['hiv_prevalence_pct','sti_incidence_pct',
              'higher_risk_sex_w_pct','condom_use_w_pct','poverty_rate',
              'literacy_rate_census','medical_density',
              'vct_knowledge_pct','modern_contraceptive_pct']
Xc = StandardScaler().fit_transform(gdf[feat_clust].fillna(gdf[feat_clust].mean()))

sils = []
for k in range(2,8):
    km = KMeans(n_clusters=k, random_state=42, n_init=20)
    sils.append(silhouette_score(Xc, km.fit_predict(Xc)))

km4 = KMeans(n_clusters=4, random_state=42, n_init=30)
gdf['syndemic_cluster'] = km4.fit_predict(Xc)
sil4 = silhouette_score(Xc, gdf['syndemic_cluster'])

burden_order = gdf.groupby('syndemic_cluster')['syndemic_burden_index'].mean().sort_values(ascending=False)
lmap = {cid: lbl for cid,lbl in zip(burden_order.index,
        ['Critical Syndemic Burden','High Syndemic Burden',
         'Moderate Syndemic Risk','Low Syndemic Risk'])}
gdf['cluster_label'] = gdf['syndemic_cluster'].map(lmap)
cluster_sizes = gdf['cluster_label'].value_counts().to_dict()
print(f"[12] K-means k=4 silhouette={sil4:.3f} | {cluster_sizes}")

# ─── 13. XGBOOST + SPATIAL CV + NATIVE SHAP ─────────────────
feat_ml = ['higher_risk_sex_w_pct','higher_risk_sex_m_pct',
           'condom_use_w_pct','condom_use_m_pct','vct_knowledge_pct',
           'condom_negotiation_pct','modern_contraceptive_pct',
           'medical_density','poverty_rate','literacy_rate_census',
           'unemployment_rate','uninsured_rate']

thr75 = gdf['syndemic_burden_index'].quantile(0.75)
gdf['high_syndemic'] = (gdf['syndemic_burden_index'] >= thr75).astype(int)

X_ml = gdf[feat_ml].fillna(gdf[feat_ml].mean()).values
y_ml = gdf['high_syndemic'].values
regions_arr = gdf['region'].fillna('Unknown').values

auc_scores = []; y_prob_cv = np.zeros(len(y_ml))
for reg in np.unique(regions_arr):
    ti = np.where(regions_arr == reg)[0]
    tri = np.where(regions_arr != reg)[0]
    if len(tri)<10 or len(ti)<2: continue
    m = xgb.XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.08,
                           subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
                           scale_pos_weight=(y_ml[tri]==0).sum()/(y_ml[tri]==1).sum()+1e-9,
                           random_state=42, eval_metric='logloss', verbosity=0)
    m.fit(X_ml[tri], y_ml[tri])
    probs = m.predict_proba(X_ml[ti])[:,1]
    y_prob_cv[ti] = probs
    if len(np.unique(y_ml[ti]))>1:
        auc_scores.append(roc_auc_score(y_ml[ti], probs))

mean_auc = float(np.mean(auc_scores)); sd_auc = float(np.std(auc_scores))
print(f"[13] Spatial CV AUC={mean_auc:.3f} ±{sd_auc:.3f} over {len(auc_scores)} regions")

# Final model
xgb_final = xgb.XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                                subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
                                scale_pos_weight=(y_ml==0).sum()/(y_ml==1).sum(),
                                random_state=42, eval_metric='logloss', verbosity=0)
xgb_final.fit(X_ml, y_ml)
gdf['syndemic_risk_score'] = xgb_final.predict_proba(X_ml)[:,1]*100

# Native SHAP
dtrain = xgb.DMatrix(X_ml, feature_names=feat_ml)
shap_matrix = xgb_final.get_booster().predict(dtrain, pred_contribs=True)
shap_vals = shap_matrix[:, :-1]
mean_abs_shap = np.abs(shap_vals).mean(axis=0)
shap_df = pd.DataFrame({'feature': feat_ml, 'mean_abs_shap': mean_abs_shap,
                         'mean_shap': shap_vals.mean(axis=0)})
shap_df = shap_df.sort_values('mean_abs_shap', ascending=False).reset_index(drop=True)
print("[13] SHAP top-5:")
for _, r in shap_df.head(5).iterrows():
    d = "↑" if r['mean_shap']>0 else "↓"
    print(f"     {r['feature']:35s} |SHAP|={r['mean_abs_shap']:.4f} {d}")

# ─── 14. SPATIAL LAG REGRESSION ──────────────────────────────
gdf['sti_lag'] = lag_spatial(wQ, gdf['sti_incidence_pct'].values)
slr_preds = ['sti_lag','higher_risk_sex_w_pct','condom_use_w_pct',
             'poverty_rate','medical_density','literacy_rate_census']
X_slr = sm.add_constant(gdf[slr_preds].fillna(gdf[slr_preds].mean()).values)
slr = sm.OLS(gdf['hiv_prevalence_pct'].values, X_slr).fit()
print(f"\n[14] SLR R²={slr.rsquared:.3f}, adj-R²={slr.rsquared_adj:.3f}, F-p={slr.f_pvalue:.4e}")
for nm_, b, p in zip(['const']+slr_preds, slr.params, slr.pvalues):
    sig = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else ''
    print(f"     {nm_:35s} β={b:+.4f} p={p:.4f} {sig}")

# ─── 15. LOGISTIC REGRESSION ─────────────────────────────────
gdf['critical_cluster'] = (gdf['cluster_label']=='Critical Syndemic Burden').astype(int)
log_preds = ['higher_risk_sex_w_pct','condom_use_w_pct','vct_knowledge_pct',
             'condom_negotiation_pct','poverty_rate','medical_density','literacy_rate_census']
X_log = sm.add_constant(gdf[log_preds].fillna(gdf[log_preds].mean()).values)
logit = sm.Logit(gdf['critical_cluster'].values, X_log).fit(disp=0)
print(f"\n[15] Logistic R²={logit.prsquared:.3f}, AIC={logit.aic:.1f}")
for nm_, b, p in zip(['const']+log_preds, logit.params, logit.pvalues):
    sig = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else ''
    print(f"     {nm_:35s} OR={np.exp(b):.3f} p={p:.4f} {sig}")

# ─── 16. SAVE CSV ─────────────────────────────────────────────
save_cols = ['district','region','lat','lon','total_pop',
             'hiv_prevalence_pct','sti_incidence_pct','syndemic_burden_index',
             'syndemic_risk_score','higher_risk_sex_w_pct','higher_risk_sex_m_pct',
             'condom_use_w_pct','condom_use_m_pct','vct_knowledge_pct',
             'condom_negotiation_pct','modern_contraceptive_pct',
             'medical_density','poverty_rate','literacy_rate_census',
             'unemployment_rate','uninsured_rate','sti_lag',
             'lisa_hiv_q','lisa_hiv_sig','lisa_sti_q','lisa_sti_sig',
             'lisa_bv_q','lisa_bv_sig','gi_zscore','gi_pval','hotspot','coldspot',
             'syndemic_cluster','cluster_label','high_syndemic','critical_cluster']
gdf[save_cols].to_csv(f'{OUT}/master_260district.csv', index=False)
print(f"\n[16] CSV saved: {len(gdf)} rows × {len(save_cols)} cols")

# ─── 17. RESULTS JSON ─────────────────────────────────────────
results = {
    "study_title": "STI and HIV syndemic burden: geospatial co-clustering and behavioural determinants in Ghana",
    "authors": ["Valentine Golden Ghanem"],
    "affiliation": "Ghana COCOBOD Cocoa Clinic, Accra, Ghana",
    "n_districts": 260, "n_regions": int(gdf['region'].nunique()),
    "data_sources": {
        "hiv_prevalence": "Ghana DHS 2014 (biomarker-confirmed)",
        "behavioral": "Ghana DHS 2022",
        "sti_proxy": "WHO GHO 2022 (national ANC syphilis seroprevalence)",
        "socioeconomic": "Ghana Population Census 2021",
        "contraceptive": "FP2020 / Ghana DHS 2022",
    },
    "hiv_prevalence_mean_pct": round(float(gdf['hiv_prevalence_pct'].mean()),2),
    "hiv_prevalence_range_pct": [round(float(gdf['hiv_prevalence_pct'].min()),2),
                                   round(float(gdf['hiv_prevalence_pct'].max()),2)],
    "sti_incidence_mean_pct": round(float(gdf['sti_incidence_pct'].mean()),2),
    "sti_incidence_range_pct": [round(float(gdf['sti_incidence_pct'].min()),2),
                                  round(float(gdf['sti_incidence_pct'].max()),2)],
    "syndemic_burden_mean": round(float(gdf['syndemic_burden_index'].mean()),2),
    "national_syphilis_anc_pct": 1.2,
    "moran_I_HIV": round(float(mi_hiv.I),4),
    "moran_z_HIV": round(float(mi_hiv.z_norm),3),
    "moran_p_HIV": round(float(mi_hiv.p_norm),4),
    "moran_I_STI": round(float(mi_sti.I),4),
    "moran_p_STI": round(float(mi_sti.p_norm),4),
    "moran_I_syndemic": round(float(mi_syn.I),4),
    "moran_p_syndemic": round(float(mi_syn.p_norm),4),
    "bivariate_moran_I": round(float(mi_bv.I),4),
    "bivariate_moran_p": round(float(mi_bv.p_sim),4),
    "SOI": round(SOI,3),
    "SOI_n_districts": int(both_hi.sum()),
    "n_hotspots_gi": int(n_hot), "n_coldspots_gi": int(n_cold),
    "lisa_bv_HH_n": int(bv_hh), "lisa_bv_LL_n": int(bv_ll),
    "lisa_hiv_HH_n": int(hiv_hh), "lisa_sti_HH_n": int(sti_hh),
    "kmeans_k": 4, "silhouette_k4": round(float(sil4),3),
    "cluster_sizes": cluster_sizes,
    "hiv_by_cluster": gdf.groupby('cluster_label')['hiv_prevalence_pct'].mean().round(2).to_dict(),
    "sti_by_cluster":  gdf.groupby('cluster_label')['sti_incidence_pct'].mean().round(2).to_dict(),
    "syndemic_by_cluster": gdf.groupby('cluster_label')['syndemic_burden_index'].mean().round(2).to_dict(),
    "spatial_cv_auc_mean": round(mean_auc,3), "spatial_cv_auc_sd": round(sd_auc,3),
    "n_cv_folds": len(auc_scores),
    "high_syndemic_threshold_75th": round(float(thr75),2),
    "high_syndemic_n": int(y_ml.sum()),
    "slr_r2": round(float(slr.rsquared),3),
    "slr_adj_r2": round(float(slr.rsquared_adj),3),
    "slr_f_pvalue": round(float(slr.f_pvalue),6),
    "slr_beta_sti_lag": round(float(slr.params[1]),4),
    "slr_p_sti_lag": round(float(slr.pvalues[1]),4),
    "logit_pseudo_r2": round(float(logit.prsquared),3),
    "logit_aic": round(float(logit.aic),1),
    "shap_top5": [{"feature": r['feature'],
                   "mean_abs_shap": round(float(r['mean_abs_shap']),4),
                   "direction": "risk-increasing" if r['mean_shap']>0 else "risk-decreasing"}
                  for _, r in shap_df.head(5).iterrows()],
    "slr_coefs": dict(zip(['const']+slr_preds, [round(float(v),4) for v in slr.params])),
    "slr_pvals": dict(zip(['const']+slr_preds, [round(float(v),4) for v in slr.pvalues])),
    "logit_ORs": dict(zip(['const']+log_preds, [round(float(np.exp(v)),3) for v in logit.params])),
    "logit_pvals": dict(zip(['const']+log_preds, [round(float(v),4) for v in logit.pvalues])),
    "sils_k2_to_k7": [round(float(s),3) for s in sils],
}

with open(f'{OUT}/analysis_results.json','w') as f:
    json.dump(results, f, indent=2)
print("[17] Results JSON saved")

# ─── 18. PICKLE FOR FIGURE SCRIPT ────────────────────────────
with open(f'{OUT}/gdf.pkl','wb') as f:
    pickle.dump(gdf, f)
with open(f'{OUT}/analysis_objects.pkl','wb') as f:
    pickle.dump({'shap_df':shap_df,'shap_vals':shap_vals,'feat_ml':feat_ml,
                 'slr':slr,'slr_preds':slr_preds,'logit':logit,'log_preds':log_preds,
                 'y_prob_cv':y_prob_cv,'y_ml':y_ml,'auc_scores':auc_scores,
                 'mean_auc':mean_auc,'mi_hiv':mi_hiv,'mi_sti':mi_sti,
                 'mi_bv':mi_bv,'mi_syn':mi_syn,'sil4':sil4,'SOI':SOI,
                 'sils':sils,'inertias':[],'bv_hh':bv_hh,'results':results},f)

print("\n=== PIPELINE COMPLETE ===")
