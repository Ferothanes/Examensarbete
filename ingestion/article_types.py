from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List

@dataclass
class NormalizedArticle:
    provider: str                  # "gdelt", "eventregistry" 
    provider_id: Optional[str]    
    url: str
    title: str
    summary: Optional[str]
    body: Optional[str]
    image_url: Optional[str]
    published_at: datetime

    source_name: Optional[str]
    source_domain: Optional[str]
    source_country: Optional[str]  
    language: Optional[str]      

    topics: List[str]            
    raw: Dict[str, Any]          
