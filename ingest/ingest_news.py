from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
from newsapi_fetcher import fetch_newsapi
from guardian_fetcher import fetch_guardian

DB_URI = "postgresql://user:pass@localhost:5432/world_news"
engine = create_engine(DB_URI)

def normalize_newsapi(data, country="us", category="general"):
    return [
        {
            "title": a.get("title"),
            "source": a["source"].get("name"),
            "published_at": a.get("publishedAt"),
            "url": a.get("url"),
            "image_url": a.get("urlToImage"),
            "country": country,
            "language": "en",
            "category": category,
            "fetched_at": datetime.utcnow()
        }
        for a in data.get("articles", [])
    ]

def normalize_guardian(data, section="technology"):
    return [
        {
            "title": a["fields"].get("headline"),
            "source": "The Guardian",
            "published_at": a.get("webPublicationDate"),
            "url": a.get("webUrl"),
            "image_url": a["fields"].get("thumbnail"),
            "country": "uk",
            "language": "en",
            "category": section,
            "fetched_at": datetime.utcnow()
        }
        for a in data.get("response", {}).get("results", [])
    ]


# Fetch news from all APIs, normalize, and store in Postgres.--------------
def ingest_all_apis():
    total_inserted = 0

    # --- NewsAPI ---
    news_data = fetch_newsapi(country="us", category="technology")
    df_newsapi = pd.DataFrame(normalize_newsapi(news_data))
    save_to_postgres(df_newsapi)
    total_inserted += len(df_newsapi)

    # --- Guardian ---
    guardian_data = fetch_guardian(section="technology")
    df_guardian = pd.DataFrame(normalize_guardian(guardian_data))
    save_to_postgres(df_guardian)
    total_inserted += len(df_guardian)

    return total_inserted


def save_to_postgres(df):
    df.to_sql("articles", engine, if_exists="append", index=False)

if __name__ == "__main__":
    # NewsAPI
    news_data = fetch_newsapi(country="us", category="technology")
    df_newsapi = pd.DataFrame(normalize_newsapi(news_data))
    save_to_postgres(df_newsapi)

    # Guardian
    guardian_data = fetch_guardian(section="technology")
    df_guardian = pd.DataFrame(normalize_guardian(guardian_data))
    save_to_postgres(df_guardian)

    print(f"Inserted {len(df_newsapi) + len(df_guardian)} rows")
