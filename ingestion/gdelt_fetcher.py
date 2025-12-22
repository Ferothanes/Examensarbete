from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional
import requests

from ingestion.article_types import NormalizedArticle

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"

def _parse_dt(dt_str: str) -> datetime:
    # GDELT typically returns ISO-ish strings; keep it robust:
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        # fallback: now (better than crash) — but log in real code
        return datetime.now(timezone.utc)

def fetch_gdelt_articles(
    query: str,
    timespan: str = "24h",
    maxrecords: int = 200,  
    sourcelang: Optional[str] = None,
    source_country: Optional[str] = None,
) -> List[NormalizedArticle]:
    
    """
    query: free-text or advanced operators; you can add filters using operators inside query.
    Example: '(economy OR inflation) sourcelang:spanish'
    """
    q = query.strip()
    if sourcelang:
        q += f" sourcelang:{sourcelang}"
    if source_country:
        # GDELT has sourceCountry; but operator usage differs across APIs.
        # We'll keep it out unless you confirm the exact operator you want to use.
        pass

    params = {
        "query": q,
        "mode": "artlist",
        "format": "json",
        "timespan": timespan,
        "sort": "datedesc",
        "maxrecords": maxrecords,
    }


    r = requests.get(GDELT_DOC_API, params=params, timeout=30)

    # GDELT sometimes returns HTML or empty responses with 200 OK
    try:
        data = r.json()
    except ValueError:
        print("GDELT returned non-JSON response")
        print("Status code:", r.status_code)
        print("Response preview:", r.text[:300])
        return []


    arts = []
    for item in data.get("articles", []) or []:
        url = item.get("url")
        title = item.get("title") or ""
        if not url or not title:
            continue

        arts.append(
            NormalizedArticle(
                provider="gdelt",
                provider_id=None,
                url=url,
                title=title,
                summary=None,
                body=None,
                image_url=item.get("socialimage") or item.get("social_image"),
                published_at=_parse_dt(item.get("seendate") or item.get("date") or ""),
                source_name=item.get("sourceCountry") or item.get("sourcecountry") or item.get("source"),
                source_domain=item.get("domain"),
                source_country=item.get("sourcecountry") or item.get("sourceCountry"),
                language=item.get("language") or item.get("lang") or item.get("Language"),
                topics=item.get("themes") or ["Unknown"],
                raw=item,
            )
        )

    return arts
