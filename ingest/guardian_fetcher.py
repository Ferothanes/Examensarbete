# guardian_fetcher.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GUARDIAN_KEY = os.getenv("GUARDIAN_KEY")

def fetch_guardian(section="technology", page_size=50):
    url = "https://content.guardianapis.com/search"
    params = {
        "section": section,
        "page-size": page_size,
        "api-key": GUARDIAN_KEY,
        "show-fields": "thumbnail,headline,body"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()
