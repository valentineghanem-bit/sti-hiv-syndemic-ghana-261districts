#!/usr/bin/env python3
"""
STI–HIV Syndemic Burden — Ghana 260 Districts
Interactive Dash dashboard: spatial clustering, behavioural determinants, SHAP.
Run: python app.py  →  http://127.0.0.1:8050
"""
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

DATA = os.path.join(os.path.dirname(__file__), "data", "master_260district.csv")
df = pd.read_csv(DATA)

# Normalise coordinate columns
if "lat" not in df.columns and "latitude" in df.columns:
    df = df.rename(columns={"latitude": "lat", "longitude": "lon"})

OUTCOMES = {
    "syndemic_burden_index": "Syndemic Burden Index (0–10)",
    "hiv_prevalence_pct":    "HIV Prevalence (%)",
    "sti_incidence_pct":     "STI Incidence (%)",
}
BEHAVIOURAL = {
    "condom_use_w_pct":      "Condom Use — Women (%)",
    "condom_use_m_pct":      "Condom Use — Men (%)",
    "vct_knowledge_pct":     "VCT Knowledge (%)",
    "higher_risk_sex_w_pct": "Higher-Risk Sex — Women (%)",
    "modern_contraceptive_pct": "Modern Contraceptive Use (%)",
    "poverty_rate":          "Poverty Rate (%)",
    "literacy_rate_census":  "Literacy Rate (%)",
}
SHAP_IMPORTANCE = {
    "condom_use_m_pct":         0.312,
    "vct_knowledge_pct":        0.287,
    "higher_risk_sex_w_pct":    0.198,
    "poverty_rate":             0.143,
    "modern_contraceptive_pct": 0.121,
    "literacy_rate_census":     0.089,
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],
                title="STI–HIV Syndemic — Ghana")
server = app.server

def kpi(label, value, color="info"):
    return dbc.Card(dbc.CardBody([
        html.P(label, className="text-muted mb-1", style={"fontSize": "0.73rem"}),
        html.H5(value, className=f"text-{color} mb-0 fw-bold"),
    ]), className="mb-2 h-100")

app.layout = dbc.Container(fluid=True, style={"backgroundColor": "#0d1117", "minHeight": "100vh"}, children=[
    dbc.Row(dbc.Col(html.H4(
        "STI & HIV Syndemic Burden — Geospatial Co-clustering & Behavioural Determinants, Ghana 260 Districts",
        className="text-center text-light py-3"))),

    dbc.Row([
        dbc.Col(kpi("HIV Moran's I", "0.768 (p<0.001)", "danger"), md=2),
        dbc.Col(kpi("STI Moran's I", "0.514 (p<0.001)", "warning"), md=2),
        dbc.Col(kpi("Bivariate LISA (HIV×STI)", "0.497 (p=0.001)", "info"), md=3),
        dbc.Col(kpi("HH Hotspot Districts", "35", "danger"), md=2),
        dbc.Col(kpi("XGBoost AUC", "0.972 ± 0.031", "success"), md=3),
    ], className="mb-3"),

    dbc.Tabs([
        # ── Spatial ─────────────────────────────────────────────────────────
        dbc.Tab(label="Spatial Co-clustering", children=[
            dbc.Row([
                dbc.Col([
                    html.Label("Outcome:", className="text-light mt-3"),
                    dcc.Dropdown(id="sbd-metric",
                                 options=[{"label": v, "value": k} for k, v in OUTCOMES.items()],
                                 value="syndemic_burden_index", clearable=False,
                                 style={"color": "#000"}),
                ], md=4),
                dbc.Col([
                    html.Label("Cluster filter:", className="text-light mt-3"),
                    dcc.Dropdown(id="cluster-filter",
                                 options=[{"label": "All", "value": "all"},
                                          {"label": "High-High (HH)", "value": "HH"},
                                          {"label": "Low-Low (LL)", "value": "LL"}],
                                 value="all", clearable=False, style={"color": "#000"}),
                ], md=3),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="syndemic-map"), md=8),
                dbc.Col(dcc.Graph(id="cluster-bar"), md=4),
            ]),
        ]),

        # ── Behavioural Determinants ─────────────────────────────────────
        dbc.Tab(label="Behavioural Determinants", children=[
            dbc.Row([
                dbc.Col([
                    html.Label("Predictor:", className="text-light mt-3"),
                    dcc.Dropdown(id="beh-x",
                                 options=[{"label": v, "value": k} for k, v in BEHAVIOURAL.items()],
                                 value="condom_use_m_pct", clearable=False,
                                 style={"color": "#000"}),
                ], md=4),
                dbc.Col([
                    html.Label("Outcome:", className="text-light mt-3"),
                    dcc.Dropdown(id="beh-y",
                                 options=[{"label": v, "value": k} for k, v in OUTCOMES.items()],
                                 value="syndemic_burden_index", clearable=False,
                                 style={"color": "#000"}),
                ], md=4),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="beh-scatter"), md=7),
                dbc.Col(dcc.Graph(id="shap-bar"), md=5),
            ]),
        ]),

        # ── District Table ───────────────────────────────────────────────
        dbc.Tab(label="District Explorer", children=[
            dbc.Row(dbc.Col([
                html.Label("Filter by Region:", className="text-light mt-3"),
                dcc.Dropdown(id="sbd-region",
                             options=[{"label": r, "value": r} for r in sorted(df.region.dropna().unique())],
                             multi=True, placeholder="All regions", style={"color": "#000"}),
            ], md=5)),
            dbc.Row(dbc.Col(dash_table.DataTable(
                id="sbd-table",
                columns=[
                    {"name": "District", "id": "district"},
                    {"name": "Region", "id": "region"},
                    {"name": "SBI", "id": "syndemic_burden_index"},
                    {"name": "HIV %", "id": "hiv_prevalence_pct"},
                    {"name": "STI %", "id": "sti_incidence_pct"},
                    {"name": "Condom % (M)", "id": "condom_use_m_pct"},
                    {"name": "VCT Know. %", "id": "vct_knowledge_pct"},
                ],
                page_size=20, sort_action="native", filter_action="native",
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "#1f2937", "color": "white"},
                style_data={"backgroundColor": "#111827", "color": "white"},
            ))),
        ]),
    ]),
])


@app.callback(Output("syndemic-map", "figure"), Output("cluster-bar", "figure"),
              Input("sbd-metric", "value"), Input("cluster-filter", "value"))
def update_spatial(metric, cluster):
    d = df.copy()
    if cluster != "all" and "lisa_bv_q" in df.columns:
        bv_map = {"HH": 1, "LL": 3}
        d = d[d.lisa_bv_q == bv_map.get(cluster, d.lisa_bv_q)]
    label = OUTCOMES[metric]
    has_coords = "lat" in d.columns and d.lat.notna().any()
    if has_coords:
        fig = px.scatter(d, x="lon", y="lat", color=metric,
                         hover_name="district", size_max=12,
                         color_continuous_scale="OrRd",
                         title=f"{label} — Spatial Distribution",
                         labels={metric: label})
    else:
        fig = px.scatter(d, x="district", y=metric, color="region",
                         title=f"{label} by District")
    fig.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                      font_color="white", margin=dict(t=40, b=10))

    cluster_counts = df.groupby("region")[metric].mean().sort_values(ascending=False).head(10)
    fig_bar = px.bar(x=cluster_counts.values, y=cluster_counts.index, orientation="h",
                     title="Mean SBI by Region (Top 10)", color=cluster_counts.values,
                     color_continuous_scale="Reds",
                     labels={"x": label, "y": "Region"})
    fig_bar.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                          font_color="white", showlegend=False, margin=dict(t=40))
    return fig, fig_bar


@app.callback(Output("beh-scatter", "figure"), Output("shap-bar", "figure"),
              Input("beh-x", "value"), Input("beh-y", "value"))
def update_beh(x_col, y_col):
    fig = px.scatter(df, x=x_col, y=y_col, color="region",
                     hover_name="district", trendline="ols",
                     title=f"{BEHAVIOURAL[x_col]} vs {OUTCOMES[y_col]}",
                     labels={x_col: BEHAVIOURAL[x_col], y_col: OUTCOMES[y_col]},
                     color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                      font_color="white", margin=dict(t=40))

    shap_df = pd.DataFrame({
        "feature": [BEHAVIOURAL.get(k, k) for k in SHAP_IMPORTANCE],
        "shap":    list(SHAP_IMPORTANCE.values()),
    }).sort_values("shap")
    fig_shap = px.bar(shap_df, x="shap", y="feature", orientation="h",
                      title="XGBoost SHAP Feature Importance",
                      color="shap", color_continuous_scale="Oranges")
    fig_shap.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                           font_color="white", showlegend=False, margin=dict(t=40))
    return fig, fig_shap


@app.callback(Output("sbd-table", "data"), Input("sbd-region", "value"))
def update_table(regions):
    d = df if not regions else df[df.region.isin(regions)]
    cols = ["district", "region", "syndemic_burden_index",
            "hiv_prevalence_pct", "sti_incidence_pct",
            "condom_use_m_pct", "vct_knowledge_pct"]
    return d[[c for c in cols if c in d.columns]].round(3).to_dict("records")


if __name__ == "__main__":
    print("Dashboard: http://127.0.0.1:8050")
    app.run(debug=False, port=8050)
