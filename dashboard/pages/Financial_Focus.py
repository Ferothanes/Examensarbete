import os
import sys
import json
import pandas as pd
import duckdb
import plotly.express as px
import streamlit as st
import textwrap
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from dashboard.styles import apply_theme, render_nav
import google.generativeai as genai

# Ensure project root is available in Python import path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

DB_FILE = os.path.join(ROOT_DIR, "world_news.duckdb")
LOGO_FILE = os.path.join(ROOT_DIR, "assets", "logo.png")

st.set_page_config(page_title="Financial Focus", layout="wide")
# Load environment variables (for GEMINI_API_KEY)
load_dotenv()
apply_theme()
render_nav()

st.title("Financial Focus")

# Intro explainer
st.markdown(
    """
    This view highlights **where financial news attention is concentrated globally**.
    Articles are filtered to business and economy-related topics and aggregated by
    source country. The goal is not to evaluate market performance, but to reveal
    **geographic focus and potential imbalance in financial reporting**.
    """
)

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
def load_articles(cutoff_iso: str | None):
    """Load articles from DuckDB and parse topics as Python lists."""
    con = duckdb.connect(DB_FILE, read_only=True)
    query = """
        SELECT title, summary, body, published_at, provider, source_country, topics, url
        FROM articles
        WHERE topics IS NOT NULL
    """
    params = []
    if cutoff_iso:
        query += " AND published_at >= ?"
        params.append(cutoff_iso)
    articles_df = con.execute(query, params).df()
    con.close()

    def parse_topics(raw):
        try:
            return json.loads(raw) if raw else []
        except Exception:
            return []

    articles_df["topics"] = articles_df["topics"].apply(parse_topics)
    articles_df["published_at"] = pd.to_datetime(
        articles_df["published_at"], utc=True, errors="coerce"
    )
    articles_df["summary"] = articles_df["summary"].fillna("")
    articles_df["source_country"] = articles_df["source_country"].fillna("Unknown")
    articles_df["url"] = articles_df["url"].fillna("")
    return articles_df


articles = load_articles(cutoff_iso)
# Split by provider for clarity
er_articles = articles[articles["provider"].str.lower() == "eventregistry"].copy()
gdelt_articles = articles[articles["provider"].str.lower() == "gdelt"].copy()

# Configure Gemini if key present
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Shared financial-related topics
focus_topics = {"business", "economy"}

# -------------------------------------------------------------------
# Q&A assistant on recent financial narratives (EventRegistry)
# Placed immediately after intro
st.subheader("Ask about recent financial narratives (EventRegistry)")
preset_questions = [
    "Which companies are most mentioned in the finance articles?",
    "What macro themes (inflation, rates, recession) dominate coverage?",
    "Based on these articles, which financial perspectives or impacts appear underrepresented or missing?",
    "Do the articles emphasize more on financial risk and uncertainty, or stability and recovery?",
    "Identify recurring financial talking points or arguments that appear across multiple articles.",
]

# preset buttons that populate the input
btn_cols = st.columns(len(preset_questions))
for col, q in zip(btn_cols, preset_questions):
    if col.button(q):
        st.session_state["finance_question"] = q

prefill = st.session_state.get("finance_question", preset_questions[0])
custom_q = st.text_input("Ask or edit your question:", value=prefill)
question = custom_q.strip()
ask_clicked = st.button("Ask question")

# Filter to EventRegistry articles that match financial topics
er_financial = er_articles[er_articles["topics"].apply(lambda ts: any(t in focus_topics for t in ts))]
er_financial = er_financial.sort_values("published_at", ascending=False)

if ask_clicked:
    if not GEMINI_API_KEY:
        st.info("Add GEMINI_API_KEY to your .env to enable the financial Q&A assistant.")
    elif er_financial.empty:
        st.info("No recent financial EventRegistry articles available for Q&A.")
    elif not question:
        st.info("Enter a question or click a preset to ask about the financial articles.")
    else:
        # Use a larger slice of financial articles while keeping prompt size reasonable
        context_rows = er_financial.head(100)
        context_snippets = [
            f"Title: {r['title']}\nSummary: {r.get('summary','')[:500]}\nPublished: {r.get('published_at')}"
            for _, r in context_rows.iterrows()
        ]
        prompt = textwrap.dedent(f"""
        You are analyzing recent financial news. Use only the provided articles.
        Answer the user's question briefly and factually.
        Question: {question}
        Articles:
        {"---".join(context_snippets)}
        """)
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            resp = model.generate_content(prompt)
            answer = resp.text if hasattr(resp, "text") else "No answer returned."
        except Exception as e:
            answer = f"Request failed: {e}"
        st.markdown(f"**Answer:** {answer}")

# -------------------------------------------------------------------
# Recent Financial Headlines (EventRegistry)
# -------------------------------------------------------------------
st.subheader("Recent Financial Headlines")
if er_financial.empty:
    st.info("No financial narratives found in EventRegistry for the selected time range.")
else:
    er_fin = er_financial.sort_values("published_at", ascending=False)
    page_size = 10
    total_pages = max(1, (len(er_fin) + page_size - 1) // page_size)
    page = st.selectbox(
        "Headlines page",
        options=list(range(1, total_pages + 1)),
        index=0,
        help="Navigate through financial headlines",
    )
    start = (page - 1) * page_size
    end = start + page_size
    page_rows = er_fin.iloc[start:end]

    for _, row in page_rows.iterrows():
        published_str = ""
        if pd.notna(row["published_at"]):
            published_str = pd.to_datetime(row["published_at"]).strftime("%Y-%m-%d %H:%M")
        meta = " | ".join(
            [x for x in [row.get("provider"), row.get("source_country"), published_str] if x]
        )
        url = row.get("url", "")
        title_md = f"[{row['title']}]({url})" if url else row["title"]
        st.markdown(
            f"- {title_md}  \n"
            f"  <span style='color:#94a3b8; font-size:0.95rem;'>{meta}</span>",
            unsafe_allow_html=True,
        )
