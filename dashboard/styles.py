import streamlit as st

__all__ = ["apply_theme", "render_nav", "apply_hover_style"]


def apply_theme():
    st.markdown("""
    <style>
    :root {
      --bg-main: #0f172a;
      --cyan: #38bdf8;
      --text-main: #e5ecf6;
      --muted: #94a3b8;
      --hover-glow: 0 0 14px rgba(56,189,248,0.35);
    }

    div[data-testid="stAppViewContainer"] {
      background-color: var(--bg-main);
      color: var(--text-main);
    }

    /* Typography system */
    [data-testid="stTitle"], h1 {
      font-size: 2.8rem !important;
      font-weight: 900 !important;
      line-height: 1.1 !important;
      color: var(--text-main) !important;
    }
    [data-testid="stHeader"], h2 {
      font-size: 2.1rem !important;
      font-weight: 800 !important;
      line-height: 1.2 !important;
      color: var(--text-main) !important;
    }
    [data-testid="stSubheader"], h3 {
      font-size: 1.6rem !important;
      font-weight: 800 !important;
      line-height: 1.25 !important;
      color: var(--text-main) !important;
    }
    [data-testid="stCaption"] {
      font-size: 0.95rem !important;
      line-height: 1.5 !important;
      color: var(--muted) !important;
    }
    div[data-testid="stMarkdown"] p,
    div[data-testid="stMarkdown"] li,
    div[data-testid="stMarkdown"] span {
      font-size: 1.05rem !important;
      line-height: 1.6 !important;
      color: var(--text-main) !important;
    }

    /* Hide Streamlit's built-in page navigation (we'll render our own links) */
    header[data-testid="stHeader"] div[role="tablist"],
    [data-testid="stSidebarNav"] {
      display: none !important;
    }


    /* Make the main title larger */
    div[data-testid="stAppViewContainer"] h1 {
      font-size: 4rem !important;
      font-weight: 900 !important;
      line-height: 1.05;
    }


    .article-title a {
      display: inline-block;
      color: var(--cyan);
      font-size: 1.4rem;
      font-weight: 700;
      text-transform: uppercase;
      text-decoration: none;
      padding: 0.45rem 0.6rem;
      border-radius: 12px;
      transition: box-shadow 0.2s ease, background 0.2s ease, color 0.2s ease;
    }

    .article-title a:hover {
      background: rgba(56,189,248,0.08);
      box-shadow: var(--hover-glow);
      color: var(--cyan);
    }

    .article-card {
      margin-top: 1rem;
      margin-bottom: 1.2rem;
      padding: 1.1rem 1.2rem;
      border-radius: 18px;
      border: 1px solid rgba(56,189,248,0.22);
      background: linear-gradient(135deg, rgba(56,189,248,0.10), rgba(15,23,42,0.92));
      box-shadow: 0 14px 26px rgba(0,0,0,0.25);
    }

    .article-meta {
      color: var(--muted);
      font-weight: 600;
      margin-top: 0.25rem;
      margin-bottom: 0.6rem;
    }

    .article-summary {
      margin-top: 0.4rem;
      margin-bottom: 0.6rem;
      padding: 0.9rem 1rem;
      border-radius: 14px;
      border: 1px solid rgba(148,163,184,0.28);
      background: rgba(148,163,184,0.08);
      color: var(--text-main);
      font-size: 1rem;
      line-height: 1.55;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }

    .article-topics {
      color: var(--muted);
      font-weight: 600;
      margin-top: 0.25rem;
    }

    /* Topic cards on analysis page */
    .topic-cards {
      display: flex;
      flex-wrap: wrap;
      gap: 0.8rem;
      align-items: stretch;
    }
    .topic-card {
      padding: 0.85rem 1rem;
      border: 1px solid rgba(56,189,248,0.25);
      border-radius: 12px;
      background: rgba(56,189,248,0.08);
      box-shadow: 0 8px 14px rgba(0,0,0,0.2);
      min-width: 180px;
      text-align: center;
    }
    .topic-card .topic {
      font-size: 2.3rem;
      font-weight: 800;
      color: #e5ecf6;
    }
    .topic-card .count {
      font-size: 2.3rem;
      font-weight: 800;
      color: #38bdf8;
    }

    /* Compact variant for smaller metric cards */
    .compact-card {
      padding: 0.65rem 0.8rem !important;
      min-width: 140px;
      border: 1px solid rgba(56,189,248,0.25);
      border-radius: 12px;
      background: rgba(56,189,248,0.08);
      box-shadow: 0 8px 14px rgba(0,0,0,0.2);
      text-align: center;
    }
    .compact-card .topic {
      font-size: 1.8rem !important;
      font-weight: 800;
      color: #e5ecf6;
    }
    .compact-card .count {
      font-size: 1.8rem !important;
      font-weight: 800;
      color: #38bdf8;
    }

    .hero-title {
      font-size: 2.6rem;
      font-weight: 800;
      margin-top: 0.1rem;
      margin-bottom: 0.1rem;
    }

    .hero-meta {
      color: var(--muted);
      font-size: 0.95rem;
      font-weight: 500;
    }

    /* Article link hover only */
    div[data-testid="stMarkdown"] a {
      display: inline-block;
      padding: 0.35rem 0.6rem;
      border-radius: 12px;
      transition: box-shadow 0.2s ease, color 0.2s ease, background 0.2s ease;
    }
                
    div[data-testid="stMarkdown"] a:hover {
      box-shadow: var(--hover-glow);
      background: rgba(56,189,248,0.08);
      color: var(--cyan);
    }

    /* Reusable blocks */
    .intro-block {
      padding: 0.5rem 0 1rem 0;
      line-height: 1.55;
      max-width: 1200px;
    }
    .metric-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.6rem 0.9rem;
      margin: 0.6rem 0 0.8rem 0;
      border-left: 4px solid #38bdf8;
      background: rgba(56,189,248,0.08);
      border-radius: 8px;
      max-width: fit-content;
    }
    .metric-badge .metric-value {
      font-size: 1.4rem;
      font-weight: 800;
      color: #e5ecf6;
      line-height: 1.2;
    }
    .metric-badge .metric-text {
      font-size: 0.95rem;
      color: #cbd5f5;
      line-height: 1.2;
    }



    /* Buttons: lock to our palette regardless of Streamlit theme */
    div.stButton > button, div.stDownloadButton > button {
      background: rgba(56,189,248,0.12) !important;
      color: var(--text-main) !important;
      border: 1px solid rgba(56,189,248,0.6) !important;
      border-radius: 10px !important;
      font-weight: 700 !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
      background: rgba(56,189,248,0.22) !important;
      color: var(--text-main) !important;
      box-shadow: var(--hover-glow);
    }

    </style>
    """, unsafe_allow_html=True)


def render_nav():
    """Consistent nav bar using buttons with Streamlit routing."""
    cols = st.columns(4)
    with cols[0]:
        if st.button("Home", use_container_width=True):
            st.switch_page("app.py")
    with cols[1]:
        if st.button("Global overview", use_container_width=True):
            st.switch_page("pages/Global_Coverage.py")
    with cols[2]:
        if st.button("Text Analysis", use_container_width=True):
            st.switch_page("pages/News_Analysis.py")
    with cols[3]:
        if st.button("Financial Focus", use_container_width=True):
            st.switch_page("pages/Financial_Focus.py")


def apply_hover_style(fig):
    """Apply a consistent hover style to Plotly figures."""
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#38bdf8",
            font=dict(color="#e5ecf6", size=17),
            align="left",
        )
    )
    return fig
