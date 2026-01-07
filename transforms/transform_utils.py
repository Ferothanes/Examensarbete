from __future__ import annotations
import re
from typing import Dict, List, Set
import pandas as pd

# --- Language normalization ---------------------------------------------------

LANGUAGE_MAP = {
    "en": "English", "eng": "English",
    "sv": "Swedish", "swe": "Swedish",
    "fr": "French", "fra": "French",
    "es": "Spanish", "spa": "Spanish",
    "de": "German", "ger": "German", "deu": "German",
    "pt": "Portuguese", "por": "Portuguese", "pt-br": "Portuguese (Brazil)",
    "ru": "Russian", "rus": "Russian",
    "zh": "Chinese", "zho": "Chinese", "cn": "Chinese",
    "ar": "Arabic", "ara": "Arabic",
    "tr": "Turkish", "tur": "Turkish",
    "it": "Italian", "ita": "Italian",
    "pl": "Polish", "pol": "Polish",
    "nl": "Dutch", "nld": "Dutch", "dut": "Dutch",
    "da": "Danish", "dan": "Danish",
    "fi": "Finnish", "fin": "Finnish",
    "no": "Norwegian", "nor": "Norwegian", "nb": "Norwegian",
    "uk": "Ukrainian", "ukr": "Ukrainian",
    "cs": "Czech", "cze": "Czech", "ces": "Czech",
    "ja": "Japanese", "jpn": "Japanese",
    "ko": "Korean", "kor": "Korean",
    "el": "Greek", "ell": "Greek",
    "he": "Hebrew", "heb": "Hebrew",
    "id": "Indonesian", "ind": "Indonesian",
    "ms": "Malay", "msa": "Malay",
    "hi": "Hindi", "hin": "Hindi",
    "bn": "Bengali", "ben": "Bengali",
    "vi": "Vietnamese", "vie": "Vietnamese",
    "th": "Thai", "tha": "Thai",
}

#Normalize language labels into human-readable names. Returns None for empty values.
def normalize_language(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    raw = str(val).strip()
    if not raw:
        return None
    lower = raw.lower()
    if lower in LANGUAGE_MAP:
        return LANGUAGE_MAP[lower]
    return raw.title()


# --- Topic categorization -----------------------------------------------------

# Canonical categories and their keyword signals. Expand here when needed!
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "business": [
        "business", "company", "companies", "market", "markets", "stock", "stocks", "equity",
        "share price", "ipo", "earnings", "revenue", "profit", "loss", "merger", "acquisition",
        "m&a", "takeover", "startup", "start-up", "venture", "ceo", "executive", "layoff",
        "investment", "investor", "funding", "valuation", "private equity", "deal"
    ],
    "economy": [
        "economy", "economic", "macro", "inflation", "gdp", "interest rate", "interest rates",
        "central bank", "federal reserve", "ecb", "boe", "boj", "unemployment", "jobs report",
        "labor market", "recession", "growth", "fiscal policy", "deficit", "trade balance",
        "cpi", "pce", "bond yield", "treasury", "monetary policy"
    ],
    "science": [
        "research", "study", "studies", "experiment", "experiments", "discovery", "discoveries",
        "peer review", "journal", "scientist", "laboratory", "lab", "academic", "evidence"
    ],
    "space": [
        "space", "nasa", "spacex", "satellite", "satellites", "rocket", "launch", "astronomy",
        "planet", "planets", "mission", "iss", "orbit", "telescope", "moon", "mars", "lunar",
        "cosmos", "spacecraft"
    ],
    "environment_climate": [
        "climate change", "emission", "emissions", "sustainability", "energy transition",
        "renewable", "renewables", "solar", "wind", "greenhouse", "carbon", "net zero",
        "wildfire", "heatwave", "flood", "drought", "hurricane", "storm", "weather event",
        "environment", "pollution", "methane", "sea level", "biodiversity"
    ],
    "society": [
        "society", "social", "migration", "immigration", "refugee", "refugees", "education",
        "school", "university", "culture", "cultural", "demographic", "demographics",
        "inequality", "poverty", "community", "housing", "crime", "justice"
    ],
    "technology": [
        "technology", "tech", "ai", "artificial intelligence", "software", "hardware", "chip",
        "semiconductor", "device", "gadget", "cloud", "data center", "cyber", "security",
        "cybersecurity", "machine learning", "automation"
    ],
    "politics": [
        "politic", "politics", "election", "elections", "government", "president", "parliament",
        "congress", "minister", "policy", "regulation", "diplomat", "diplomacy", "vote",
        "voting", "campaign", "senate"
    ],
    "sports": [
        "sport", "sports", "football", "soccer", "nba", "fifa", "olympic", "tennis", "golf",
        "cricket", "baseball", "basketball", "tournament", "match", "game", "league", "cup"
    ],
    "health": [
        "health", "covid", "virus", "vaccine", "hospital", "medicine", "medical", "doctor",
        "nurse", "disease", "outbreak", "pandemic", "pharma", "drug", "clinical trial",
        "mental health", "public health"
    ],
}

# Alias mapping for direct topic strings
ALIASES = {
    "environment & climate": "environment_climate",
    "environment and climate": "environment_climate",
    "environment": "environment_climate",
    "climate": "environment_climate",
}

ALLOWED = set(CATEGORY_KEYWORDS.keys())


#Count keyword hits per category in the provided text (case-insensitive). Returns a dict of category -> score.
def _score_categories(text: str) -> Dict[str, int]:
    txt = (text or "").lower()
    scores: Dict[str, int] = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        count = 0
        for kw in keywords:
            if kw in txt:
                count += 1
        if count > 0:
            scores[cat] = count
    return scores


def _select_categories(scores: Dict[str, int]) -> List[str]:
    """
    Pick top categories based on scores.
    Rule: keep the top category; include a second if it is within 1 point of the top.
    This matches: 5 vs 1 -> keep one; 4 vs 3 -> keep both.
    """
    if not scores:
        return []

    ordered = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    top_score = ordered[0][1]
    if top_score <= 0:
        return []

    selected = []
    for cat, score in ordered:
        if score < top_score - 1:
            break
        selected.append(cat)
        if len(selected) == 2:
            break
    return selected


#Compute category labels from free text (title + summary/body).
def categorize_text(text: str) -> List[str]:
    scores = _score_categories(text)
    return _select_categories(scores)


#Normalize provider topics into categories.
#If text_blob is provided and no categories are derived, fallback to keyword scoring.
def normalize_topics(raw_topics: List[str], text_blob: str | None = None) -> List[str]:
    out = set()

    for t in raw_topics or []:
        t_norm = (t or "").lower().strip()
        if not t_norm:
            continue
        if t_norm in ALIASES:
            out.add(ALIASES[t_norm])
            continue
        if t_norm in ALLOWED:
            out.add(t_norm)
            continue
        # map by keyword signals inside provided topic string
        for cat, kws in CATEGORY_KEYWORDS.items():
            if any(k in t_norm for k in kws):
                out.add(cat)
                break

    if not out and text_blob:
        out.update(categorize_text(text_blob))

    # Keep at most two categories to avoid over-tagging
    return sorted(out)[:2]


# --- Framing analysis helpers -------------------------------------------------

FRAME_GROUPS: Dict[str, List[str]] = {
    "Conflict & War": [
        "war", "armed conflict", "military conflict", "battle", "combat",
        "offensive", "counteroffensive", "troops", "military deployment",
        "frontline", "airstrike", "missile strike", "shelling",
        "invasion", "occupation"
    ],
    "Terrorism & Security": [
        "terrorist attack", "terrorism", "extremist group", "militant",
        "insurgent", "suicide bombing", "mass shooting",
        "security forces", "counterterrorism", "homeland security",
        "radicalization"
    ],
    "Sanctions & Pressure": [
        "economic sanctions", "trade sanctions", "financial sanctions",
        "embargo", "asset freeze", "travel ban", "export controls",
        "blacklist", "secondary sanctions", "boycott"
    ],
    "Humanitarian Impact": [
        "humanitarian crisis", "civilian casualties", "civilian deaths",
        "refugees", "internally displaced", "displacement",
        "humanitarian aid", "aid delivery", "evacuation",
        "famine", "food insecurity", "medical supplies"
    ],
    "Technology": [
        "artificial intelligence", "machine learning", "AI model",
        "large language model", "software system",
        "cyberattack", "cyber warfare", "cybersecurity breach",
        "data breach", "semiconductor", "chip manufacturing",
        "surveillance technology"
    ],
    "Climate & Environment": [
        "climate change", "global warming", "greenhouse gas",
        "greenhouse gases", "carbon emissions", "CO2 emissions",
        "net zero", "renewable energy", "energy transition",
        "fossil fuels", "pollution", "environmental damage",
        "climate policy"
    ],
}


def count_frames(text: str) -> dict:
    """Count article-level matches per framing group inside a text blob."""
    txt = (text or "").lower()
    scores = {}
    for frame, kws in FRAME_GROUPS.items():
        matched = any(re.search(rf"\b{re.escape(kw)}\b", txt) for kw in kws)
        scores[frame] = 1 if matched else 0
    return scores


# --- Similarity clustering helpers -------------------------------------------
# For this im using the article title not the body, reason = most of the time the title is more to the point and does not have opinion

def _token_set(text: str) -> Set[str]:
    """Lightweight tokenization for similarity checks on titles."""
    tokens = re.split(r"\W+", (text or "").lower())
    return {t for t in tokens if len(t) >= 3}

# Jaccard = (gemensamma ord) / (alla unika ord)
def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / len(a | b)

# delar upp varje titel i ord, jämför rubrikerna med varann, grupperar liknande artiklar 
def cluster_articles_by_title(
    frame: pd.DataFrame, limit: int = 300, threshold: float = 0.35 #max 300 articles being compared, must be atleast 35% similar
) -> List[list]:

    # removes articles with no title, sorts and only takes limit rules set above
    subset = frame.dropna(subset=["title"]).sort_values("published_at", ascending=False).head(limit)
    tokens = [_token_set(t) for t in subset["title"]] #each title made into seperate words
    n = len(tokens) # n = amount of articles
    parent = list(range(n)) #parent keeps check of what articles belong together 

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # compares article titles 
    for i in range(n):
        for j in range(i + 1, n):
            if _jaccard(tokens[i], tokens[j]) >= threshold:
                union(i, j)

    clusters = {}
    for idx, row in enumerate(subset.itertuples(index=False)):
        root = find(idx)
        clusters.setdefault(root, []).append(row)

    return [members for members in clusters.values() if len(members) > 1]
