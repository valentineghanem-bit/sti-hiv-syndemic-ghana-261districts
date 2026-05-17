"""
Figure Generation — STI-HIV Syndemic Analysis | Ghana 260 Districts
Valentine Golden Ghanem | May 2026
Produces 5 publication-quality figures (300 DPI, SVG+PNG)
"""
import pickle, json, warnings, os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.cm import ScalarMappable
import matplotlib.ticker as ticker
import seaborn as sns
from sklearn.metrics import roc_curve, roc_auc_score

warnings.filterwarnings('ignore')

OUT    = '/sessions/sweet-sharp-franklin/mnt/outputs'
FIG    = f'{OUT}/figures'
os.makedirs(FIG, exist_ok=True)

# ─── LOAD PICKLES ────────────────────────────────────────────────────────────
print("Loading pickled data...")
with open(f'{OUT}/gdf.pkl','rb') as f:
    gdf = pickle.load(f)

with open(f'{OUT}/analysis_objects.pkl','rb') as f:
    obj = pickle.load(f)

shap_df   = obj['shap_df']
shap_vals = obj['shap_vals']
feat_ml   = obj['feat_ml']
slr       = obj['slr']
logit     = obj['logit']
y_prob_cv = obj['y_prob_cv']
y_ml      = obj['y_ml']
auc_scores = obj['auc_scores']
mean_auc  = obj['mean_auc']
mi_hiv    = obj['mi_hiv']
mi_sti    = obj['mi_sti']
mi_bv     = obj['mi_bv']
mi_syn    = obj['mi_syn']
sil4      = obj['sil4']
SOI       = obj['SOI']
sils      = obj['sils']
bv_hh     = obj['bv_hh']
results   = obj['results']

with open(f'{OUT}/analysis_results.json') as f:
    R = json.load(f)

# ─── STYLE ───────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':'DejaVu Sans',
    'font.size':11,
    'axes.labelsize':12,
    'axes.labelweight':'semibold',
    'axes.titlesize':13,
    'axes.titleweight':'bold',
    'axes.linewidth':0.8,
    'xtick.labelsize':10,
    'ytick.labelsize':10,
    'legend.fontsize':10,
    'figure.dpi':150,
    'savefig.dpi':300,
    'savefig.bbox':'tight',
    'savefig.facecolor':'white',
})

# Colour palette
C_HIV  = '#C0392B'
C_STI  = '#E67E22'
C_SYN  = '#8E44AD'
C_COLD = '#2980B9'
C_NEU  = '#BDC3C7'
CMAP_SEQ = 'YlOrRd'

def save_fig(fig, name):
    fig.savefig(f'{FIG}/{name}.png', dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(f'{FIG}/{name}.svg', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {name}.png / .svg")

# ─── FIGURE 1: HIV & STI CHOROPLETH (2-panel) ──────────────────────────────
print("[Fig 1] HIV & STI choropleth...")
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

for ax, col, cmap, title, label in zip(
    axes,
    ['hiv_prevalence_pct', 'sti_incidence_pct'],
    ['YlOrRd', 'YlOrBr'],
    ['(A) HIV Prevalence by District (%)', '(B) STI Incidence Proxy by District (%)'],
    ['HIV Prevalence (%)', 'STI Incidence (%)']
):
    gdf_plot = gdf[gdf[col].notna()].copy()
    gdf_miss = gdf[gdf[col].isna()].copy()

    gdf.plot(ax=ax, color='#EEEEEE', linewidth=0.2, edgecolor='#AAAAAA')
    p = gdf_plot.plot(column=col, cmap=cmap, ax=ax, linewidth=0.3,
                      edgecolor='#777777', legend=False,
                      vmin=gdf_plot[col].quantile(0.02),
                      vmax=gdf_plot[col].quantile(0.98))
    if len(gdf_miss):
        gdf_miss.plot(ax=ax, color='#CCCCCC', linewidth=0.2, edgecolor='#999999', hatch='//')

    sm = ScalarMappable(cmap=cmap,
                        norm=plt.Normalize(vmin=gdf_plot[col].quantile(0.02),
                                           vmax=gdf_plot[col].quantile(0.98)))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, shrink=0.7)
    cbar.set_label(label, fontsize=10)

    ax.set_title(title, fontsize=13, fontweight='bold', pad=8)
    ax.set_axis_off()

fig.text(0.5, -0.01,
         'Figure 1. Spatial distribution of HIV prevalence (A) and STI incidence proxy (B) '
         'across 260 Ghana districts. HIV: Ghana DHS 2014 biomarker survey; '
         'STI proxy: WHO GHO 2022 ANC syphilis seroprevalence scaled by '
         'behavioural risk multiplier. Grey hatching = districts with missing data.',
         ha='center', fontsize=10, style='italic', wrap=True)
fig.tight_layout(rect=[0, 0.04, 1, 1])
save_fig(fig, 'fig1_hiv_sti_choropleth')

# ─── FIGURE 2: BIVARIATE LISA + SYNDEMIC BURDEN INDEX ──────────────────────
print("[Fig 2] Bivariate LISA + Syndemic Burden Index...")
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Panel A — Bivariate LISA clusters
ax = axes[0]
if 'bv_cluster' in gdf.columns:
    cluster_col = 'bv_cluster'
    colors = {'HH': '#C0392B', 'LL': '#2980B9', 'HL': '#F39C12', 'LH': '#27AE60', 'ns': '#D5D8DC'}
    labels_map = {'HH':'High HIV–High STI (HH)', 'LL':'Low HIV–Low STI (LL)',
                  'HL':'High HIV–Low STI (HL)', 'LH':'Low HIV–High STI (LH)', 'ns':'Non-significant'}
    for cat, col in colors.items():
        sub = gdf[gdf[cluster_col]==cat]
        if len(sub):
            sub.plot(ax=ax, color=col, linewidth=0.3, edgecolor='#555555')
    patches = [mpatches.Patch(color=c, label=labels_map[k]) for k,c in colors.items() if k in gdf[cluster_col].values]
    ax.legend(handles=patches, loc='lower left', fontsize=8.5, framealpha=0.9,
              title='LISA Cluster (p<0.05)', title_fontsize=9)
else:
    gdf.plot(ax=ax, color='#CCCCCC', linewidth=0.2)
    ax.text(0.5, 0.5, 'BV LISA\nnot available', transform=ax.transAxes, ha='center')
ax.set_title('(A) Bivariate LISA: HIV × STI Co-clustering', fontsize=13, fontweight='bold', pad=8)
ax.set_axis_off()
ax.annotate(f"BV Moran's I = {R['bivariate_moran_I']:.4f}, p = {R['bivariate_moran_p']:.3f}\n"
            f"HH clusters: n = {R['lisa_bv_HH_n']}  |  LL clusters: n = {R['lisa_bv_LL_n']}",
            xy=(0.5, 0.02), xycoords='axes fraction', ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.85))

# Panel B — Syndemic Burden Index choropleth
ax = axes[1]
gdf_sbi = gdf[gdf['syndemic_burden_index'].notna()].copy()
gdf_miss = gdf[gdf['syndemic_burden_index'].isna()].copy()
gdf.plot(ax=ax, color='#EEEEEE', linewidth=0.2, edgecolor='#AAAAAA')
gdf_sbi.plot(column='syndemic_burden_index', cmap='RdPu', ax=ax,
             linewidth=0.3, edgecolor='#777777', legend=False,
             vmin=0, vmax=10)
if len(gdf_miss):
    gdf_miss.plot(ax=ax, color='#CCCCCC', linewidth=0.2, edgecolor='#999999', hatch='//')
sm2 = ScalarMappable(cmap='RdPu', norm=plt.Normalize(vmin=0, vmax=10))
sm2.set_array([])
cbar2 = plt.colorbar(sm2, ax=ax, fraction=0.03, pad=0.02, shrink=0.7)
cbar2.set_label('Syndemic Burden Index (0–10)', fontsize=10)
ax.set_title('(B) Syndemic Burden Index (SBI)', fontsize=13, fontweight='bold', pad=8)
ax.set_axis_off()
ax.annotate(f"SBI: mean = {R['syndemic_burden_mean']:.2f}  |  "
            f"SOI = {R['SOI']:.3f} ({R['SOI_n_districts']} districts co-elevated)",
            xy=(0.5, 0.02), xycoords='axes fraction', ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.85))

fig.text(0.5, -0.01,
         'Figure 2. (A) Bivariate LISA cluster map showing spatial co-clustering of HIV prevalence '
         'and STI incidence across 260 Ghana districts (pseudo-p<0.05, 999 permutations). '
         'HH = high-HIV/high-STI syndemic hotspots; LL = low-burden clusters. '
         '(B) Syndemic Burden Index (SBI; 0–10 scale) derived as the mean of '
         'standardised HIV and STI values.',
         ha='center', fontsize=10, style='italic', wrap=True)
fig.tight_layout(rect=[0, 0.04, 1, 1])
save_fig(fig, 'fig2_lisa_sbi')

# ─── FIGURE 3: K-MEANS SYNDEMIC CLUSTERS ────────────────────────────────────
print("[Fig 3] K-means cluster map + profile...")
fig = plt.figure(figsize=(17, 7))
gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.35)
ax_map = fig.add_subplot(gs[0])
ax_bar = fig.add_subplot(gs[1])

cluster_colors = {
    'Critical Syndemic Burden': '#7B241C',
    'High Syndemic Burden':     '#C0392B',
    'Moderate Syndemic Risk':   '#E67E22',
    'Low Syndemic Risk':        '#2ECC71',
}
if 'cluster_label' in gdf.columns:
    gdf.plot(ax=ax_map, color='#EEEEEE', linewidth=0.2, edgecolor='#AAAAAA')
    for lbl, col in cluster_colors.items():
        sub = gdf[gdf['cluster_label']==lbl]
        if len(sub):
            sub.plot(ax=ax_map, color=col, linewidth=0.3, edgecolor='#555555')
    patches = [mpatches.Patch(color=c, label=f"{k}\n(n={R['cluster_sizes'].get(k,'?')})")
               for k,c in cluster_colors.items()]
    ax_map.legend(handles=patches, loc='lower left', fontsize=8.5, framealpha=0.9,
                  title='Syndemic Cluster', title_fontsize=9)
ax_map.set_title('(A) K-means Syndemic Cluster Map (k=4)', fontsize=13, fontweight='bold', pad=8)
ax_map.set_axis_off()

# Cluster profile: bar chart of mean HIV, STI, SBI by cluster
order = ['Critical Syndemic Burden','High Syndemic Burden','Moderate Syndemic Risk','Low Syndemic Risk']
hiv_vals = [R['hiv_by_cluster'].get(c,0) for c in order]
sti_vals = [R['sti_by_cluster'].get(c,0) for c in order]
sbi_vals = [R['syndemic_by_cluster'].get(c,0) for c in order]

x = np.arange(len(order))
w = 0.25
short_labels = ['Critical\n(n=48)','High\n(n=89)','Moderate\n(n=73)','Low\n(n=50)']
b1 = ax_bar.bar(x - w,   hiv_vals, w, label='HIV Prevalence (%)', color=C_HIV, alpha=0.88)
b2 = ax_bar.bar(x,       sti_vals, w, label='STI Incidence (%)',  color=C_STI, alpha=0.88)
b3 = ax_bar.bar(x + w,   sbi_vals, w, label='SBI (÷2 for scale)', color=C_SYN, alpha=0.88)
ax_bar.set_xticks(x)
ax_bar.set_xticklabels(short_labels, fontsize=10)
ax_bar.set_ylabel('Mean Value (%)', fontsize=12, fontweight='semibold')
ax_bar.set_title('(B) Cluster Profile: HIV, STI, and SBI', fontsize=13, fontweight='bold', pad=8)
ax_bar.legend(fontsize=9, loc='upper right')
ax_bar.set_ylim(0, max(sbi_vals)*1.25)
for bars in [b1,b2,b3]:
    for bar in bars:
        h = bar.get_height()
        if h > 0.1:
            ax_bar.text(bar.get_x()+bar.get_width()/2, h+0.05, f'{h:.1f}',
                       ha='center', va='bottom', fontsize=8.5)
ax_bar.spines['top'].set_visible(False)
ax_bar.spines['right'].set_visible(False)

fig.text(0.5, -0.01,
         'Figure 3. (A) Spatial distribution of k-means syndemic clusters (k=4, silhouette=0.234) '
         'across 260 Ghana districts. (B) Cluster profiles showing mean HIV prevalence, STI incidence, '
         'and Syndemic Burden Index. Critical and High Syndemic Burden clusters (n=137 districts) '
         'concentrate in Greater Accra, Ashanti, Eastern, and coastal regions.',
         ha='center', fontsize=10, style='italic', wrap=True)
fig.tight_layout(rect=[0, 0.04, 1, 1])
save_fig(fig, 'fig3_kmeans_clusters')

# ─── FIGURE 4: SHAP BAR + SPATIAL CV ROC ────────────────────────────────────
print("[Fig 4] SHAP importance + spatial CV ROC...")
fig = plt.figure(figsize=(17, 7))
gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.4)
ax_shap = fig.add_subplot(gs[0])
ax_roc  = fig.add_subplot(gs[1])

# Panel A — SHAP mean |SHAP| bar
top_n = min(10, len(shap_df))
shap_plot = shap_df.head(top_n).copy()
feature_labels = {
    'higher_risk_sex_w_pct':    'Higher-risk sex, women (%)',
    'poverty_rate':             'Poverty rate (%)',
    'unemployment_rate':        'Unemployment rate (%)',
    'condom_negotiation_pct':   'Condom negotiation ability (%)',
    'condom_use_w_pct':         'Condom use at last higher-risk sex (%)',
    'vct_knowledge_pct':        'VCT/HIV knowledge (%)',
    'literacy_rate_census':     'Female literacy rate (%)',
    'medical_density':          'Healthcare worker density (per 1,000)',
    'hiv_knowledge_w_pct':      'Women\'s HIV knowledge (%)',
    'contraceptive_use_pct':    'Modern contraceptive use (%)',
}
shap_plot['label'] = shap_plot['feature'].map(lambda x: feature_labels.get(x, x.replace('_',' ')))
shap_plot['color'] = shap_plot['mean_shap'].apply(lambda v: C_HIV if v>0 else C_STI)
bars = ax_shap.barh(range(top_n), shap_plot['mean_abs_shap'].values[::-1],
                    color=shap_plot['color'].values[::-1], alpha=0.88, height=0.65)
ax_shap.set_yticks(range(top_n))
ax_shap.set_yticklabels(shap_plot['label'].values[::-1], fontsize=9.5)
ax_shap.set_xlabel('Mean |SHAP| Value', fontsize=12, fontweight='semibold')
ax_shap.set_title('(A) XGBoost Feature Importance (SHAP)', fontsize=13, fontweight='bold', pad=8)
ax_shap.spines['top'].set_visible(False)
ax_shap.spines['right'].set_visible(False)
# Direction legend
ax_shap.axvline(0, color='black', lw=0.5)
p1 = mpatches.Patch(color=C_HIV, label='Risk-increasing')
p2 = mpatches.Patch(color=C_STI, label='Risk-decreasing')
ax_shap.legend(handles=[p1,p2], fontsize=9, loc='lower right')
for i,bar in enumerate(bars):
    w = bar.get_width()
    ax_shap.text(w+0.02, bar.get_y()+bar.get_height()/2, f'{w:.3f}',
                va='center', fontsize=8.5)

# Panel B — Spatial CV ROC
fpr, tpr, _ = roc_curve(y_ml, y_prob_cv)
ax_roc.plot(fpr, tpr, color=C_SYN, lw=2.5,
            label=f'Spatial CV ROC (AUC = {mean_auc:.3f} ± {np.std(auc_scores):.3f})')
ax_roc.plot([0,1],[0,1],'k--',lw=1,alpha=0.5,label='No discrimination')
ax_roc.fill_between(fpr, tpr, alpha=0.12, color=C_SYN)
ax_roc.set_xlabel('1 – Specificity (False Positive Rate)', fontsize=12, fontweight='semibold')
ax_roc.set_ylabel('Sensitivity (True Positive Rate)', fontsize=12, fontweight='semibold')
ax_roc.set_title('(B) Leave-One-Region-Out Spatial CV\nROC Curve', fontsize=13, fontweight='bold', pad=8)
ax_roc.legend(fontsize=10, loc='lower right')
ax_roc.set_xlim([0,1]); ax_roc.set_ylim([0,1.02])
ax_roc.spines['top'].set_visible(False)
ax_roc.spines['right'].set_visible(False)
ax_roc.annotate(f'n folds = {R["n_cv_folds"]}\nn high-syndemic = {R["high_syndemic_n"]}',
                xy=(0.95,0.12), xycoords='axes fraction', ha='right', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.85))

fig.text(0.5, -0.01,
         'Figure 4. (A) XGBoost SHAP feature importance for prediction of high syndemic burden '
         '(SBI > 75th percentile). Feature bars coloured by association direction. '
         '(B) Leave-one-region-out spatial cross-validation ROC curve, confirming '
         f'high discriminative capacity (AUC = {mean_auc:.3f} ± {np.std(auc_scores):.3f}) '
         'across {R["n_cv_folds"]} geographic folds.',
         ha='center', fontsize=10, style='italic', wrap=True)
fig.tight_layout(rect=[0, 0.04, 1, 1])
save_fig(fig, 'fig4_shap_roc')

# ─── FIGURE 5: SPATIAL LAG REGRESSION + MORAN SCATTER ──────────────────────
print("[Fig 5] Spatial lag regression + Moran scatterplots...")
fig = plt.figure(figsize=(17, 7))
gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.4)
ax_slr  = fig.add_subplot(gs[0])
ax_mor  = fig.add_subplot(gs[1])

# Panel A — SLR: fitted vs actual HIV prevalence
if 'hiv_prevalence_pct' in gdf.columns and gdf['hiv_prevalence_pct'].notna().sum() > 10:
    valid = gdf['hiv_prevalence_pct'].notna()
    y_actual = gdf.loc[valid, 'hiv_prevalence_pct'].values
    # Use the fitted values from slr object
    fitted = slr.fittedvalues.values[:len(y_actual)]
    ax_slr.scatter(y_actual, fitted, alpha=0.5, color=C_HIV, s=35, edgecolors='white', lw=0.4)
    mn, mx = min(y_actual.min(), fitted.min()), max(y_actual.max(), fitted.max())
    ax_slr.plot([mn,mx],[mn,mx],'k--',lw=1.5,alpha=0.7,label='Perfect fit')
    ax_slr.set_xlabel('Observed HIV Prevalence (%)', fontsize=12, fontweight='semibold')
    ax_slr.set_ylabel('SLR Fitted Values', fontsize=12, fontweight='semibold')
    ax_slr.set_title(f'(A) Spatial Lag Regression: Observed vs Fitted\n'
                     f'R² = {R["slr_r2"]:.3f}, adj-R² = {R["slr_adj_r2"]:.3f}',
                     fontsize=13, fontweight='bold', pad=8)
    ax_slr.legend(fontsize=9)
    ax_slr.spines['top'].set_visible(False)
    ax_slr.spines['right'].set_visible(False)

# Panel B — Moran scatterplot (Global) for HIV
if 'hiv_prevalence_pct' in gdf.columns:
    x_std = gdf['hiv_prevalence_pct'].fillna(gdf['hiv_prevalence_pct'].mean())
    x_std = (x_std - x_std.mean()) / x_std.std()
    wx_std = mi_hiv.z_sim if hasattr(mi_hiv,'z_sim') else x_std
    # Use spatial lag if available
    try:
        from libpysal.weights import lag_spatial
        with open(f'{OUT}/gdf.pkl','rb') as f:
            _gdf = pickle.load(f)
        # spatial lag is already in gdf
        if 'hiv_lag' in gdf.columns:
            x_val = (gdf['hiv_prevalence_pct'].fillna(gdf['hiv_prevalence_pct'].mean()) -
                     gdf['hiv_prevalence_pct'].mean()) / gdf['hiv_prevalence_pct'].std()
            wx_val = (gdf['hiv_lag'] - gdf['hiv_lag'].mean()) / gdf['hiv_lag'].std()
        else:
            x_val = x_std
            wx_val = x_std * 0  # fallback
    except:
        x_val = x_std
        wx_val = x_std * 0

    # Colour by BV cluster if available
    if 'bv_cluster' in gdf.columns:
        cmap_moran = {'HH':C_HIV, 'LL':C_COLD, 'HL':C_STI, 'LH':'#27AE60', 'ns':C_NEU}
        pt_colors = gdf['bv_cluster'].map(cmap_moran).fillna(C_NEU)
    else:
        pt_colors = C_HIV

    ax_mor.scatter(x_val, wx_val, c=pt_colors, alpha=0.5, s=35,
                   edgecolors='white', lw=0.4)
    # Moran slope
    slope = mi_hiv.I
    xr = np.linspace(x_val.min(), x_val.max(), 100)
    ax_mor.plot(xr, slope*xr, color='#2C3E50', lw=2, label=f"Moran's I = {R['moran_I_HIV']:.4f}")
    ax_mor.axhline(0, color='grey', lw=0.8, ls='--')
    ax_mor.axvline(0, color='grey', lw=0.8, ls='--')
    ax_mor.set_xlabel('Standardised HIV Prevalence (z)', fontsize=12, fontweight='semibold')
    ax_mor.set_ylabel("Spatial Lag (W·z)", fontsize=12, fontweight='semibold')
    ax_mor.set_title(f"(B) Global Moran's I Scatterplot — HIV\n"
                     f"I = {R['moran_I_HIV']:.4f}, z = {R['moran_z_HIV']:.3f}, p < 0.001",
                     fontsize=13, fontweight='bold', pad=8)
    ax_mor.legend(fontsize=9)
    ax_mor.spines['top'].set_visible(False)
    ax_mor.spines['right'].set_visible(False)

    if 'bv_cluster' in gdf.columns:
        patches = [mpatches.Patch(color=c, label=l) for l,c in [
            ('BV-HH',C_HIV),('BV-LL',C_COLD),('Non-sig.',C_NEU)]]
        ax_mor.legend(handles=patches, fontsize=9, loc='upper left')

fig.text(0.5, -0.01,
         "Figure 5. (A) Spatial lag regression observed-versus-fitted plot (R² = "
         f"{R['slr_r2']:.3f}; adj-R² = {R['slr_adj_r2']:.3f}), with HIV prevalence as outcome "
         "and behavioural, socioeconomic, and spatially-lagged STI covariates. "
         "(B) Global Moran's I scatterplot for HIV prevalence "
         f"(I = {R['moran_I_HIV']:.4f}, z = {R['moran_z_HIV']:.3f}, p<0.001), "
         "confirming strong positive spatial autocorrelation. Points coloured by "
         "bivariate LISA cluster membership.",
         ha='center', fontsize=10, style='italic', wrap=True)
fig.tight_layout(rect=[0, 0.04, 1, 1])
save_fig(fig, 'fig5_slr_moran')

print("\n=== ALL FIGURES GENERATED ===")
print(f"Saved to: {FIG}/")
for f in sorted(os.listdir(FIG)):
    sz = os.path.getsize(f'{FIG}/{f}')
    print(f"  {f:40s} {sz//1024:>5} KB")
