from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import List, Optional

from eventregistry import EventRegistry, QueryArticlesIter, QueryItems
from ingestion.article_types import NormalizedArticle
from transforms.transform_utils import categorize_text

def _parse_er_dt(dt_str: str) -> datetime:
    # ER usually returns "YYYY-MM-DD" or iso strings
    try:
        return datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def _extract_topics(art: dict, fallback_keywords: List[str]) -> List[str]:
    """Pick topics from ER article; avoid broad keyword fallbacks."""
    cats = art.get("categories") or art.get("categoriesEng") or []
    topic_strings: List[str] = []
    for c in cats:
        if isinstance(c, dict):
            topic_strings.append(c.get("label") or c.get("name") or c.get("uri") or "")
        elif isinstance(c, str):
            topic_strings.append(c)
    return [t.lower() for t in topic_strings if t]

def fetch_eventregistry_articles(
    keywords: List[str],
    category: Optional[str] = None,     # e.g. "Business"
    lang: Optional[str] = None,         # e.g. "eng", "deu" (ER uses 3-letter)
    max_items: int = 100,
) -> List[NormalizedArticle]:
    api_key = os.getenv("EVENTREGISTRY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing EVENTREGISTRY_API_KEY env var")

    er = EventRegistry(apiKey=api_key, allowUseOfArchive=False)

    q = QueryArticlesIter(
        keywords=QueryItems.OR(keywords) if len(keywords) > 1 else keywords[0],
        categoryUri=er.getCategoryUri(category) if category else None,
        lang=lang
    )

    out: List[NormalizedArticle] = []
    for art in q.execQuery(er, sortBy="date", maxItems=max_items):
        url = art.get("url")
        title = art.get("title") or ""
        if not url or not title:
            continue

        source = art.get("source", {}) or {}
        source_country = (art.get("location") or {}).get("country") or source.get("country")
        if not source_country:
            source_country = "Unknown"

        text_blob = f"{title} {art.get('body') or art.get('summary') or ''}"
        topics = categorize_text(text_blob)
        if not topics:
            topics = _extract_topics(art, keywords if category is None else [category])

        out.append(
            NormalizedArticle(
                provider="eventregistry",
                provider_id=art.get("uri"),
                url=url,
                title=title,
                summary=art.get("summary"),
                body=art.get("body") or art.get("summary"),
                published_at=_parse_er_dt(art.get("dateTime") or art.get("date") or ""),
                source_name=source.get("title"),
                source_domain=source.get("uri"),
                source_country=source_country,
                language=art.get("lang") or art.get("language"),
                image_url=None,
                topics=topics,
                raw=art,
            )
        )
    return out
