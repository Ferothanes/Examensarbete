from __future__ import annotations

import duckdb
import hashlib
import json
from typing import List
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

# -------- ingestion (external data) --------
from ingestion.gdelt_fetcher import fetch_gdelt_articles
from ingestion.eventregistry_fetcher import fetch_eventregistry_articles

# -------- processing (your logic) ----------
from transforms.transform_utils import normalize_topics, normalize_language
# -------- storage --------------------------
from .schema import DDL
from ingestion.article_types import NormalizedArticle

DB_PATH = "world_news.duckdb"


# -------------------------------------------------
# Utilities
# -------------------------------------------------

def article_id_from_url(url: str) -> str:
    """Stable ID for deduplication"""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def ensure_schema(con: duckdb.DuckDBPyConnection):
    """Create tables if they don’t exist"""
    con.execute(DDL)

# -------------------------------------------------
# Storage
# -------------------------------------------------

def upsert_articles(
    con: duckdb.DuckDBPyConnection,
    articles: List[NormalizedArticle]
) -> int:
    """
    Normalize topics, translate (if needed), and store articles.
    Deduplication is handled via article_id primary key.
    """
    if not articles:
        return 0

    rows = []

    for a in articles:
        # Normalize URL a bit to avoid dupes on trailing spaces or slashes
        normalized_url = (a.url or "").strip()
        if normalized_url.endswith("/"):
            normalized_url = normalized_url[:-1]

        article_id = article_id_from_url(normalized_url)

        # ---- normalize topics (skip for gdelt to keep original themes) ----
        provider_lower = (a.provider or "").lower()
        text_blob = f"{a.title or ''} {a.summary or ''}"
        topics = a.topics if provider_lower == "gdelt" else normalize_topics(a.topics, text_blob=text_blob)

        rows.append({
            "article_id": article_id,
            "provider": a.provider,
            "provider_id": a.provider_id,
            "url": normalized_url,
            "title": a.title,
            "summary": a.summary,
            "body": a.body,
            "image_url": a.image_url,
            "published_at": a.published_at,
            "source_name": a.source_name,
            "source_domain": a.source_domain,
            "source_country": a.source_country,
            "language": normalize_language(a.language),
            "topics": json.dumps(topics)
        })

    df_rows = pd.DataFrame(rows).drop_duplicates(subset=["article_id"])
    con.register("rows", df_rows)

    con.execute("""
        INSERT INTO articles (
            article_id, provider, provider_id, url, title, summary, body, image_url, published_at,
            source_name, source_domain, source_country, language, topics
        )
        SELECT
            article_id, provider, provider_id, url, title, summary, body, image_url, published_at,
            source_name, source_domain, source_country, language, topics
        FROM rows
        ON CONFLICT(article_id) DO NOTHING
    """)

    return len(rows)


# -------------------------------------------------
# Main ingestion pipeline
# -------------------------------------------------

def ingest() -> int:
    """
    Orchestrates ingestion from all sources.
    """
    con = duckdb.connect(DB_PATH)
    ensure_schema(con)

    total_inserted = 0

    # ---------------- GDELT ----------------
    gdelt_articles = fetch_gdelt_articles(
        query="(economy OR business OR finance OR technology OR politics OR sports OR health)",
        timespan="24h",
        maxrecords=250 # reduce faster testing
    )

    total_inserted += upsert_articles(con, gdelt_articles)

    # ------------ Event Registry ------------
    er_articles = fetch_eventregistry_articles(
        keywords=["economy", "technology", "politics", "sports", "health"],
        max_items=250
    )

    total_inserted += upsert_articles(con, er_articles)

    con.close()
    return total_inserted


# -------------------------------------------------
# Dagster entrypoint compatibility
# -------------------------------------------------
def ingest_all_apis() -> int:
    """Alias for Dagster: run all ingestions and return inserted count."""
    return ingest()


# -------------------------------------------------
# CLI entrypoint
# -------------------------------------------------

if __name__ == "__main__":
    inserted = ingest()
    print(f"Ingested {inserted} new articles into DuckDB")
