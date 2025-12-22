import os
import sys
import streamlit as st
import duckdb
import json
import pandas as pd
import html
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()

# Make project root importable when running via `streamlit run dashboard/app.py`
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from styles import apply_theme, render_nav

DB_FILE = os.path.join(os.path.dirname(__file__), "../world_news.duckdb")
LOGO_FILE = os.path.join(os.path.dirname(__file__), "../assets/logo.png")

# ---------------- Page config ----------------
st.set_page_config(
    page_title="World News Dashboard",
    layout="wide"
)

apply_theme()

# ---------------- Helper functions ----------------

TIME_FILTER_OPTIONS = {
    "Last 24 hours": timedelta(hours=24),
    "Last 7 days": timedelta(days=7),
    "Last 30 days": timedelta(days=30),
    "All time": None
}

# ---------------- Data loading ----------------
@st.cache_data(ttl=600)
def load_data():
    con = duckdb.connect(DB_FILE, read_only=True)
    df = con.execute("""
        SELECT
            title,
            summary,
            url,
            image_url,
            published_at,
            provider,
            source_name,
            source_country,
            language,
            topics
        FROM articles
        ORDER BY published_at DESC
        LIMIT 3000
    """).df()
    con.close()

    def parse_topics(x):
        try:
            return json.loads(x) if x else []
        except Exception:
            return []

    df["topics"] = df["topics"].apply(parse_topics)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    return df


df = load_data()

# ---------------- Header ----------------
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
render_nav()
st.title("World News Dashboard")
st.caption("Global, multilingual news aggregated from multiple trusted sources")
st.markdown(
    """
<div class="intro-block">
  <p><strong>Why this dashboard exists:</strong> In a time of constant global conflict, information overload, and growing concerns around misinformation, understanding how the world is being reported is more important than ever. News does not only shape what we know - it shapes what we notice, what we ignore, and how we understand global events.</p>
  <p><strong>What we combine:</strong> We merge two distinct sources to give a fuller view.</p>
  <ul style="margin-top:0.25rem; margin-bottom:0.5rem; padding-left:1.1rem;">
    <li><strong>EventRegistry</strong>: rich topic signals and categorization, but source locations can be sparse.</li>
    <li><strong>GDELT</strong>: strong source country/location coverage, but no topics; we lean on GDELT for geography and EventRegistry for topics.</li>
  </ul>
  <p><strong>How to read it:</strong> Instead of focusing on individual articles, we surface patterns in coverage across regions, languages, and time. Use the filters to see where attention is concentrated, where it is fading, and which stories may be underrepresented.</p>
</div>
"""
, unsafe_allow_html=True
)

# ---------------- Sidebar filters ----------------
if os.path.exists(LOGO_FILE):
    st.sidebar.image(LOGO_FILE, use_container_width=True)
st.sidebar.header("Filters")
search_query = st.sidebar.text_input("Search article titles")

all_topics = sorted({t for ts in df["topics"] for t in ts})
selected_topics = st.sidebar.multiselect(
    "Categories",
    all_topics,
    format_func=lambda t: t.replace("_", " ").title()
)

all_countries = sorted(df["source_country"].dropna().unique())
selected_countries = st.sidebar.multiselect("Countries", all_countries)

all_languages = sorted(df["language"].dropna().unique())
selected_languages = st.sidebar.multiselect("Languages", all_languages)

selected_time_range = st.sidebar.radio(
    "Published time",
    list(TIME_FILTER_OPTIONS.keys()),
    index=list(TIME_FILTER_OPTIONS.keys()).index("All time")
)

providers = sorted(df["provider"].dropna().unique())
selected_providers = st.sidebar.multiselect("Provider", providers)

# Back to top in sidebar
st.sidebar.markdown(
    """
    <div style="margin-top: 1rem; margin-bottom: 1rem;">
        <a href="#top" style="color:#38bdf8; font-weight:700; text-decoration:none;">
            ↑ Back to top
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Filtering logic ----------------
filtered_df = df.copy()

time_window = TIME_FILTER_OPTIONS[selected_time_range]
if time_window is not None:
    cutoff = datetime.now(timezone.utc) - time_window
    filtered_df = filtered_df[
        filtered_df["published_at"] >= cutoff
    ]

if search_query:
    q = search_query.lower()
    filtered_df = filtered_df[
        filtered_df["title"].str.lower().str.contains(q, na=False)
    ]

if selected_topics:
    filtered_df = filtered_df[
        filtered_df["topics"].apply(lambda ts: any(t in ts for t in selected_topics))
    ]

if selected_countries:
    filtered_df = filtered_df[filtered_df["source_country"].isin(selected_countries)]

if selected_languages:
    filtered_df = filtered_df[filtered_df["language"].isin(selected_languages)]

if selected_providers:
    filtered_df = filtered_df[filtered_df["provider"].isin(selected_providers)]

# ---------------- Display articles ----------------
st.markdown(f"""
<div class="hero-card">
  <div class="hero-title">Top News</div>
  <div class="hero-meta">{len(filtered_df)} articles | {selected_time_range}</div>
</div>
""", unsafe_allow_html=True)

for _, row in filtered_df.iterrows():
    display_title = row["title"]
    display_summary = row["summary"]
    display_url = row["url"]
    display_image = row.get("image_url", None)

    published_str = ""
    if pd.notna(row["published_at"]):
        published_str = pd.to_datetime(row["published_at"]).strftime("%Y-%m-%d %H:%M")

    meta_parts = [
        # For GDELT we don’t have a domain; show "Unknown" as the source name.
        "Unknown domain" if str(row["provider"]).lower() == "gdelt" else row["source_name"],
        row["provider"],
        published_str
    ]

    if row["source_country"]:
        meta_parts.append(str(row["source_country"]))

    if pd.notna(row["language"]):
        meta_parts.append(row["language"])

    safe_meta = [str(x) for x in meta_parts if x is not None]
    meta_text = " | ".join(safe_meta)

    summary_html = ""
    if display_summary:
        preview = display_summary[:500]
        if len(display_summary) > 500:
            preview += "..."
        summary_html = f'<div class="article-summary">{html.escape(preview)}</div>'

    topics_html = ""
    if row["topics"]:
        topics_html = f'<div class="article-topics">Topics: {html.escape(", ".join(row["topics"]))}</div>'

    st.markdown(
        f"""
<div class="article-card">
  <div class="article-title"><a href="{html.escape(display_url)}" target="_blank">{html.escape(display_title)}</a></div>
  <div class="article-meta">{html.escape(meta_text)}</div>
  {f"<img src='{html.escape(str(display_image))}' style='width:400px; height:auto; border-radius:8px; margin:0.5rem 0;'/>" if display_image else ""}
  {summary_html}
  {topics_html}
</div>
""",
        unsafe_allow_html=True,
    )
