# News Dashboard — Documentation

## What this is
A small, beginner-friendly project that fetches world news, stores it in DuckDB, and presents insights in a Streamlit dashboard. Dagster is used for scheduling and orchestration; ingestion scripts fetch data from sources.

---

## Dataflow (very short) 🔁

ingestion scripts --> transforms --> DuckDB (world_news.duckdb) --> Streamlit dashboard / Dagster jobs

## Project Structure (visualized)

```
Examensarbete_repository/
├── ingestion/
│   ├── __init__.py
│   ├── ingest_news.py
│   ├── article_types.py
│   ├── schema.py
│   ├── eventregistry_fetcher.py
│   └── gdelt_fetcher.py
├── dagster_code/
│   └── repository.py
├── dashboard/
│   ├── pages/
│   │    ├── Financial_Focus.py
│   │    ├── Global_Coverage.py
│   │    └── News_Analysis.py
│   ├── app.py   
│   └── styles.py
├── transforms/
│   └── transform_utils.py
├── tests/
│   └── unit_test.py
├── assets/
├── exploration.ipynb
├── world_news.duckdb
├── README.MD
├── requirements.txt
├── Dockerfile
└── .env
```


---

## Quick folder map (important parts) 🔎
- `ingestion/` — scripts that fetch and save news (e.g., `ingest_news.py`, fetchers)
- `transforms/` — data normalization helpers
- `dashboard/` — Streamlit app (`app.py`) + pages
- `dagster_code/` — Dagster repository and job definitions
- `world_news.duckdb` — local database file (created/updated by ingestion)
- `requirements.txt` — Python dependencies

---

## Prerequisites ✅
- Python 3.10+ (Windows instructions shown)
- Docker (optional but recommended for container run)
- Git (optional)

---

## Setup (Windows) — Fast path ⚡
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

## Common commands (beginner-friendly) 🛠️

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

---

## Mini glossary ✏️
- **Ingestion**: fetch news from sources and save raw data.
- **Transforms**: clean/normalize data for analysis.
- **Dagster**: scheduler and orchestrator for regular ingestion runs.
- **DuckDB**: a local analytical database file used for storing articles.

---

If you'd like, I can make this even more minimal (one-page cheat-sheet) or add an `.env.example` template — tell me which you'd prefer.