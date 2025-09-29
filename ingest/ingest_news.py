import os
import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")
DB_URI = "postgresql://user:pass@localhost:5432/world_news"
engine = create_engine(DB_URI)

def fetch_news(country="us", category="general"):
    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": country, "category": category, "apiKey": API_KEY}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()

def normalize_articles(data, country="us", category="general"):
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

def save_to_postgres(df):
    df.to_sql("articles", engine, if_exists="append", index=False)

if __name__ == "__main__":
    data = fetch_news(country="us", category="technology")
    df = pd.DataFrame(normalize_articles(data))
    save_to_postgres(df)
    print(f"Inserted {len(df)} rows")
