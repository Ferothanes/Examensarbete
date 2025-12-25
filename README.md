# News Dashboard — Documentation

## What this is
A small, beginner-friendly project that fetches world news, stores it in DuckDB, and presents insights in a Streamlit dashboard. Dagster is used for scheduling and orchestration; ingestion scripts fetch data from sources.

## Project scope 
Why this dashboard exists: In a time of constant global conflict, information overload, and growing concerns around misinformation, understanding how the world is being reported is more important than ever. News does not only shape what we know - it shapes what we notice, what we ignore, and how we understand global events.
### What we combine

This dashboard brings together two complementary news sources to provide a more complete view of global coverage:

- **EventRegistry** — Rich article text and topic signals, making it well suited for narrative and framing analysis. Geographic origin is limited or inconsistent.
- **GDELT** — Strong country and location metadata, ideal for analyzing where news attention is concentrated, but with little to no topic or article body information.

Each source is used for what it does best: **GDELT for geographic coverage**, **EventRegistry for topics and narratives**.

### How to read the dashboard

Rather than focusing on individual articles, the dashboard highlights **patterns in coverage** across regions, languages, and time. Use the filters to explore where attention is concentrated, which topics dominate, how narratives persist, and which stories may be underrepresented.


---

## Dataflow (very short) 

ingestion scripts --> transforms --> DuckDB (world_news.duckdb) --> Streamlit dashboard / Dagster jobs

---

## Quick folder map (important parts) 
- `ingestion/` — scripts that fetch and save news (e.g., `ingest_news.py`, fetchers)
- `transforms/` — data normalization helpers
- `dashboard/` — Streamlit app (`app.py`) + pages
- `dagster_code/` — Dagster repository and job definitions
- `world_news.duckdb` — local database file (created/updated by ingestion)
- `requirements.txt` — Python dependencies

---

## Prerequisites 
- Python 3.10+ (Windows instructions shown)
- Docker (optional but recommended for container run)
- Git (optional)

---

## Setup (Windows) — Fast path
1. Create and activate venv:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install requirements:

```powershell
pip install -r requirements.txt
```

3. Ensure a `.env` file exists in the project root with any required configuration (if you plan to use Docker or external DB). If there's a `.env.example`, copy it and fill values.

---

## Common commands (beginner-friendly) 

- Run ingestion (fetch & save news to DuckDB):

```powershell
python -m ingestion.ingest_news
```

- Inspect DuckDB (optional):

```powershell
duckdb world_news.duckdb
SELECT COUNT(*) FROM articles;
```

- Run the Streamlit dashboard locally:

```powershell
streamlit run dashboard/app.py
# open http://localhost:8501
```

- Run Dagster (developer UI and manual runs):

```powershell
dagster dev -f dagster_code/repository.py
# open Dagster web UI (usually http://127.0.0.1:3000)
# Find job: `news_job` → Launch Run
```

- Docker (build and run the app in a container):

```powershell
docker build -t news-dashboard .
docker run --rm -p 8501:8501 --env-file .env news-dashboard
# open http://localhost:8501
```

- Run tests:

```powershell
python -m pytest
```

---

## Quick troubleshooting ⚠️
- If a command fails, ensure your venv is activated and run `pip install -r requirements.txt`.
- If ports are in use (8501 for Streamlit), stop the conflicting service or change the port.
- Make sure `.env` exists when using Docker or services that depend on env vars.

> Tip: Run ingestion first to populate `world_news.duckdb` before exploring the dashboard.
