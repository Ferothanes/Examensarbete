from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List

@dataclass
class NormalizedArticle:
    provider: str                  # "gdelt" | "eventregistry" | ...
    provider_id: Optional[str]     # provider-specific id if exists
    url: str
    title: str
    summary: Optional[str]
    body: Optional[str]
    image_url: Optional[str]
    published_at: datetime

    source_name: Optional[str]
    source_domain: Optional[str]
    source_country: Optional[str]  # ISO2 if possible (e.g. "SE")
    language: Optional[str]        # ISO639-1 if possible (e.g. "sv", "en")

    topics: List[str]              # normalized topics like ["business","finance"]
    raw: Dict[str, Any]            # original payload for debugging / future enrichment
