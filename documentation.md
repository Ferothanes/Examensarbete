# Project Structure (visualized)

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
│   ├── app.py
│   ├── pages/
│   └── styles.py
├── transforms/
│   └── transform_utils.py
├── assets/
├── exploration.ipynb
├── world_news.duckdb
├── README.MD
├── requirements.txt
├── Dockerfile
└── .env
```

## What each key file does (summeries)

- `dashboard/app.py` — Home page. Loads recent articles from DuckDB, shows sidebar filters (search, time window, country, language, provider, topics), and renders the article list with summaries and links.
- `dashboard/pages/Global_Coverage.py` — GDELT-focused view: world map of article volume by source country, coverage imbalance cards, and top publishing domains per country with a media concentration badge.
- `dashboard/pages/News_Analysis.py` — EventRegistry-focused view: top topics, clustering of repeated narratives (similar headlines), framing keyword analysis over time, and download options for clusters.
- `dashboard/styles.py` — Central theme and typography. Controls colors, fonts, button styles, reusable blocks (intro, badges), and a helper to apply consistent hover styling to Plotly charts.
- `transforms/transform_utils.py` — Shared data helpers: language normalization, topic categorization, framing keyword groups/counters, and headline clustering utilities.
- `ingestion/ingest_news.py` — Main ingestion pipeline: calls the fetchers, normalizes data (topics, language), and upserts into DuckDB.
- `ingestion/eventregistry_fetcher.py` — Pulls articles from EventRegistry, extracts topics/bodies, and maps them into the common article format.
- `ingestion/gdelt_fetcher.py` — Pulls articles from GDELT, normalizes fields (titles, country, language), and maps them into the common article format.
- `ingestion/article_types.py` — Dataclass schema for a normalized article (shared structure for ingestion).
- `ingestion/schema.py` — DuckDB table definition and indexes for storing articles.
- `dagster_code/repository.py` — Dagster repository entrypoint (for scheduling/orchestration if used).
- `world_news.duckdb` — Local DuckDB database file containing ingested articles.
- `Dockerfile` — Container definition to run the dashboard in a consistent environment.
- `requirements.txt` — Python dependencies needed to run the project (dashboard, ingestion, Dagster).
- `.env` — Environment variables (e.g., API keys) loaded at runtime; not committed to version control.

## Key files with tools used

- dashboard/app.py � Streamlit UI, DuckDB + pandas for filtering, HTML snippets for cards/links, hover styling via styles.py.
- dashboard/pages/Global_Coverage.py � Streamlit, DuckDB + pandas, Plotly (map and bars), shared hover style.
- dashboard/pages/News_Analysis.py � Streamlit, DuckDB + pandas/NumPy, Plotly, clustering/framing helpers from transform_utils, shared hover style.
- dashboard/styles.py � CSS/theme via Streamlit injection; provides the Plotly hover-style helper.
- 	ransforms/transform_utils.py � pandas + regex for language normalization, topic categorization, framing counters, headline clustering.
- ingestion/ingest_news.py � DuckDB writes, pandas batch prep, uses helpers from transform_utils.
- ingestion/eventregistry_fetcher.py � EventRegistry SDK, topic helper.
- ingestion/gdelt_fetcher.py � requests HTTP client, datetime parsing/normalization.
- ingestion/article_types.py � Python dataclasses/typing for article schema.
- ingestion/schema.py � DuckDB DDL/indexes.
- dagster_code/repository.py � Dagster orchestration entrypoint.
- world_news.duckdb � DuckDB data file.
- Dockerfile � Container: Python base, installs requirements, runs Streamlit app.
- equirements.txt � Python deps for dashboard/ingestion/Dagster.
- .env � Env vars (API keys/settings), not versioned.

