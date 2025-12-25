import os
import sys
import json
import pandas as pd
import duckdb
import plotly.express as px
import streamlit as st
from datetime import datetime, timezone, timedelta
import html
import numpy as np
from collections import Counter

from transforms.transform_utils import FRAME_GROUPS, cluster_articles_by_title, count_frames

# Ensure project root is available in Python import path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from dashboard.styles import apply_theme, render_nav, apply_hover_style

# File paths
DB_FILE = os.path.join(ROOT_DIR, "world_news.duckdb")
LOGO_FILE = os.path.join(ROOT_DIR, "assets", "logo.png")

st.set_page_config(page_title="Text Analysis", layout="wide")
apply_theme()

# Meny ------------------------------------------
render_nav()

st.title("Text Analysis")
st.markdown("This page breaks down what the news is actually about: " \
"dominant topics, recurring storylines, and the narratives that shape coverage.")


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


# Load articles from DuckDB and preprocess fields.
# Cached for 10 minutes to avoid unnecessary DB reads.
@st.cache_data(ttl=600)
def load_articles(cutoff_iso: str | None):
    con = duckdb.connect(DB_FILE, read_only=True)
    # Execute SQL query to fetch relevant columns
    query = """
        SELECT
            title,
            summary,
            body,
            published_at,
            source_country,
            topics,
            provider
        FROM articles
        WHERE topics IS NOT NULL
    """
    params = []
    if cutoff_iso:
        query += " AND published_at >= ?"
        params.append(cutoff_iso)
    df = con.execute(query, params).df()
    con.close()
    # parse topics
    def parse_topics(x):
        try:
            return json.loads(x) if x else []
        except Exception:
            return []
    df["topics"] = df["topics"].apply(parse_topics)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df["summary"] = df["summary"].fillna("")
    df["body"] = df["body"].fillna("")
    return df

df = load_articles(cutoff_iso)
# Restrict analysis to EventRegistry only
df = df[df["provider"].str.lower() == "eventregistry"]

# explode topics. Convert list of topics into one row per topic
exploded = df.explode("topics").dropna(subset=["topics"]).copy()
exploded["topics"] = exploded["topics"].astype(str)
exploded["source_country"] = exploded["source_country"].fillna("Unknown")

# Most written topics header (for clarity on bottom chart)
st.subheader("Most Written Topics (EventRegistry only)")

topic_counts = (
    exploded[exploded["topics"].str.lower() != "unknown"]
    .groupby("topics")
    .size()
    .reset_index(name="article_count")
    .rename(columns={"topics": "topic"})
    .sort_values("article_count", ascending=False)
)
fig_topic_total = px.bar(
    topic_counts,
    x="article_count",
    y="topic",
    orientation="h",
    text="article_count",
    color="article_count",
    color_continuous_scale=[[0, "#38bdf8"], [1, "#ef4444"]],
)
fig_topic_total.update_layout(
    plot_bgcolor="#0f172a",
    paper_bgcolor="#0f172a",
)
apply_hover_style(fig_topic_total)
fig_topic_total.update_traces(textposition="outside")
fig_topic_total.update_xaxes(
    title_text="Article count",
    tickfont=dict(size=14),
    title_font=dict(size=17),
    showline=True,
    linecolor="#94a3b8",
    showgrid=False,
    zeroline=False,
)
fig_topic_total.update_yaxes(
    title_text="",
    tickfont=dict(size=14),
    title_font=dict(size=17),
    autorange="reversed",
    showline=True,
    linecolor="#94a3b8",
    showgrid=False,
    zeroline=False,
)
st.plotly_chart(fig_topic_total, use_container_width=True)
framing_df = df.copy()
framing_df["body"] = framing_df["body"].fillna("")
# If body is empty, fall back to summary text
framing_df["body"] = np.where(
    framing_df["body"].str.len() == 0,
    framing_df["summary"],
    framing_df["body"],
)
frame_counts = framing_df["body"].apply(count_frames)
frame_totals = pd.DataFrame(list(frame_counts)).fillna(0)
frame_totals["published_at"] = framing_df["published_at"].values

# Aggregate weekly for totals
frame_totals["week"] = frame_totals["published_at"].dt.to_period("W").apply(lambda r: r.start_time)
weekly = frame_totals.groupby("week")[list(FRAME_GROUPS.keys())].sum().reset_index()

# Total dominance across selected time range
st.subheader("Dominant News Framings in Recent Coverage")
st.markdown(
    "This chart shows which narrative frames receive the most attention across the selected time period. "
    "Keyword frequency is used as a proxy for framing emphasis, highlighting how news coverage prioritizes "
    "certain perspectives such as conflict, security, sanctions, or humanitarian impact. "
    "The analysis reflects attention allocation rather than sentiment or intent."
)
total_counts = weekly[list(FRAME_GROUPS.keys())].sum().reset_index()
total_counts.columns = ["frame", "count"]
bar_fig = px.bar(
    total_counts.sort_values("count", ascending=False),
    x="frame",
    y="count",
    title="",
    labels={"frame": "Frame", "count": "Keyword hits"},
)
bar_fig.update_layout(
    plot_bgcolor="#0f172a",
    paper_bgcolor="#0f172a",
    title_text="",
    bargap=0.35,
    width=1100,
)
bar_fig.update_traces(
    hovertemplate="<b>%{x}</b><br>Keyword hits: %{y:,}<extra></extra>"
)
apply_hover_style(bar_fig)
st.plotly_chart(bar_fig, use_container_width=False)

total_sum = total_counts["count"].sum()
if total_sum > 0:
    frame_cards = []
    for _, row in total_counts.sort_values("count", ascending=False).iterrows():
        pct = (row["count"] / total_sum) * 100
        frame_cards.append(
            f"<div class='compact-card'><div class='topic'>{row['frame']}</div>"
            f"<div class='count'>{pct:.1f}%</div>"
            f"<div style='color:#94a3b8; font-size:1rem; font-weight:700;'>Hits: {int(row['count']):,}</div></div>"
        )
    st.markdown(
        f"<div class='topic-cards'>{''.join(frame_cards)}</div>",
        unsafe_allow_html=True,
    )

# Move repeated narratives to bottom
clusters = cluster_articles_by_title(df, limit=350, threshold=0.35)
clusters_sorted = sorted(clusters, key=lambda c: len(c), reverse=True)

if clusters_sorted:
    st.subheader("Repeated Narratives Across Articles")
    st.markdown(
        "Articles are clustered when their headlines share at least 35% of keywords. "
        "This table shows the repeated narrative (headline snippet), cluster size, "
        "a topic hint, and a few example titles.\n\n"
        "- **Cluster size**: how many near-duplicate or highly similar headlines we found.\n"
        "- **Topic hint**: the most common category inside the cluster.\n"
        "- **Examples**: sample headlines so you can quickly see the shared narrative."
    )

    def _mode_topic(rows):
        bag = Counter()
        for r in rows:
            for t in getattr(r, "topics", []) or []:
                bag[t] += 1
        return bag.most_common(1)[0][0] if bag else ""

    top_clusters = clusters_sorted[:6]
    table = pd.DataFrame({
        "cluster_size": [len(c) for c in top_clusters],
        "topic_hint": [_mode_topic(c) for c in top_clusters],
        "examples": [" | ".join([m.title for m in c[:3]]) for c in top_clusters],
    })

    st.dataframe(table, use_container_width=True)
