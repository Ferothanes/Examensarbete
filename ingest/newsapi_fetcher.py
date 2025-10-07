# newsapi_fetcher.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")

def fetch_newsapi(country="us", category="general"):
    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": country, "category": category, "apiKey": API_KEY}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()
