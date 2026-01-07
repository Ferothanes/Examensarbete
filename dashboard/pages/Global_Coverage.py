import os
import sys
import duckdb
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime, timezone, timedelta

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from dashboard.styles import apply_theme, render_nav, apply_hover_style

DB_FILE = os.path.join(ROOT_DIR, "world_news.duckdb")
LOGO_FILE = os.path.join(ROOT_DIR, "assets", "logo.png")

st.set_page_config(page_title="Global Coverage", layout="wide")
apply_theme()

render_nav()

st.title("Global Coverage")
st.markdown("A global snapshot of where news is produced — " \
"showing which countries dominate coverage and which barely register in the data. (GDELT only)")

if os.path.exists(LOGO_FILE):
    st.sidebar.image(LOGO_FILE, use_container_width=True)

TIME_FILTER_OPTIONS = {
    "Last 24 hours": timedelta(hours=24),
    "Last 7 days": timedelta(days=7),
    "Last 30 days": timedelta(days=30),
    "All time": None,
}

selected_time_range = st.sidebar.radio(
    "Published time",
    list(TIME_FILTER_OPTIONS.keys()),
    index=list(TIME_FILTER_OPTIONS.keys()).index("All time"),
)
time_window = TIME_FILTER_OPTIONS[selected_time_range]
cutoff = datetime.now(timezone.utc) - time_window if time_window else None
cutoff_iso = cutoff.isoformat() if cutoff else None

@st.cache_data(ttl=600)
def load_country_counts(cutoff_iso: str | None):
    """Load GDELT article counts per source country."""
    con = duckdb.connect(DB_FILE, read_only=True)
    query = """
        SELECT source_country, published_at
        FROM articles
        WHERE source_country IS NOT NULL
          AND lower(provider) = 'gdelt'
    """
    params = []
    if cutoff_iso:
        query += " AND published_at >= ?"
        params.append(cutoff_iso)
    country_df = con.execute(query, params).df()
    con.close()
    country_df["published_at"] = pd.to_datetime(country_df["published_at"], utc=True, errors="coerce")
    counts = country_df.groupby("source_country").size().reset_index(name="article_count")
    return counts[counts["source_country"].notna()]


@st.cache_data(ttl=600)
def load_domain_counts(cutoff_iso: str | None):
    """Load article counts per (country, domain) across all providers."""
    con = duckdb.connect(DB_FILE, read_only=True)
    query = """
        SELECT source_country, source_domain, published_at
        FROM articles
        WHERE source_country IS NOT NULL
          AND source_domain IS NOT NULL
    """
    params = []
    if cutoff_iso:
        query += " AND published_at >= ?"
        params.append(cutoff_iso)
    domain_df = con.execute(query, params).df()
    con.close()
    domain_df["published_at"] = pd.to_datetime(domain_df["published_at"], utc=True, errors="coerce")
    return (
        domain_df.groupby(["source_country", "source_domain"])
        .size()
        .reset_index(name="article_count")
    )

country_counts = load_country_counts(cutoff_iso)
domain_counts = load_domain_counts(cutoff_iso)

total_articles = country_counts["article_count"].sum()
country_counts["share"] = (country_counts["article_count"] / total_articles * 100).round(1)

# Label coverage tiers by volume (low/mid/high based on quantiles)
low_cut = country_counts["article_count"].quantile(0.33)
high_cut = country_counts["article_count"].quantile(0.66)

def coverage_label(count: float) -> str:
    if count >= high_cut:
        return "High coverage"
    if count <= low_cut:
        return "Low coverage"
    return "Medium coverage"

country_counts["coverage_label"] = country_counts["article_count"].apply(coverage_label)

# Match the Financial Focus globe palette
colorscale = [
    [0.0, "#1e3a8a"],
    [1.0, "#38bdf8"],
]

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("Coverage Imbalance by Country (GDELT)")
    country_cards = []
    for _, row in country_counts.sort_values("article_count", ascending=False).head(10).iterrows():
        country_name = row["source_country"] if pd.notna(row["source_country"]) else "Unknown"
        country_cards.append(
            f"<div class='topic-card compact-card'>"
            f"<div class='topic'>{country_name}</div>"
            f"<div class='count'>{row['share']:.1f}%</div>"
            f"<div style='color:#94a3b8; font-size:0.95rem; font-weight:700;'>Articles: {int(row['article_count']):,}</div>"
            f"</div>"
        )

    st.markdown(
        f"<div class='topic-cards'>{''.join(country_cards)}</div>",
        unsafe_allow_html=True,
    )

with col2:
    fig = go.Figure(
        go.Choropleth(
            locations=country_counts["source_country"],
            z=country_counts["article_count"],
            locationmode="country names",
            colorscale=colorscale,
            colorbar_title="Articles",
            marker_line_color="rgba(229,236,246,0.25)",
            marker_line_width=0.5,
            customdata=country_counts[["coverage_label", "share"]],
            hovertemplate=(
                "<b>%{location}</b><br>"
                "<span style='color:#38bdf8;'>%{customdata[0]}</span><br>"
                "<span style='font-size:0.9em;'>Articles: %{z:,}</span><br>" 
                "<span style='font-size:0.9em;'>Share: %{customdata[1]:.1f}%</span>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_geos(
        projection_type="orthographic",
        projection_rotation=dict(lon=0, lat=0),
        showcountries=True,
        showcoastlines=False,
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=650,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    apply_hover_style(fig)
    st.plotly_chart(fig, use_container_width=True)

# Top publishing domains per country (all sources)
st.subheader("Top Publishing Domains per Country (All Sources)")
st.markdown(
    "Shows which news domains contribute the most articles for the selected country. "
    "A small number of dominant domains can indicate concentrated media influence or "
    "repeated framing within coverage."
)
# Available countries based on domain counts
available_countries = sorted(domain_counts["source_country"].dropna().unique())
# Default to United Kingdom if available, else first option
default_index = 0
if "United Kingdom" in available_countries:
    default_index = available_countries.index("United Kingdom")
selected_country = st.selectbox(
    "Select country",
    available_countries,
    index=default_index if available_countries else None,
)

if selected_country:
    country_domains = domain_counts[domain_counts["source_country"] == selected_country]
    top_domains = country_domains.sort_values("article_count", ascending=False).head(10)
    if not top_domains.empty:
        total = country_domains["article_count"].sum()
        top3_share = (
            country_domains.sort_values("article_count", ascending=False)
            .head(3)["article_count"]
            .sum()
        )
        top3_pct = (top3_share / total * 100).round(1) if total else 0
        if top3_pct >= 60:
            concentration_level = "High concentration"
        elif top3_pct >= 35:
            concentration_level = "Moderate concentration"
        else:
            concentration_level = "Low concentration"
        top_domains = top_domains.assign(
            share=lambda d: (d["article_count"] / total * 100).round(1)
        )

        st.markdown(
            f"""
            <div class="metric-badge">
                <div class="metric-value">{top3_pct}%</div>
                <div class="metric-text">
                    of all articles in <b>{selected_country}</b><br>
                    come from the <b>top 3 domains</b><br>
                    <span style="color:#38bdf8; font-weight:700;">{concentration_level}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        dom_fig = px.bar(
            top_domains.sort_values("article_count"),
            x="article_count",
            y="source_domain",
            orientation="h",
            text="share",
            labels={
                "article_count": "Number of articles",
                "source_domain": "Publishing domain",
                "share": "Share (%)",
            },
        )

        dom_fig.update_traces(
            texttemplate="%{text}%",
            textposition="outside",
            marker_line_width=0,
        )

        dom_fig.update_layout(
            height=420,
            margin=dict(l=120, r=40, t=20, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(148,163,184,0.15)",
                zeroline=False,
            ),
            yaxis=dict(
                autorange="reversed",
                tickfont=dict(size=13),
            ),
            showlegend=False,
        )
        apply_hover_style(dom_fig)
        st.plotly_chart(dom_fig, use_container_width=True)
    else:
        st.info("No domain data available for this country in the selected time window.")
