✅ Docker + Postgres + pgAdmin → data storage
✅ ingest scripts → fetching and saving news data
✅ Dagster → scheduling and orchestration
✅ .env + requirements.txt → config and dependencies

## DOCKER 
- docker build -t news-dashboard .
- docker run --rm -p 8501:8501 --env-file .env news-dashboard
- http://localhost:8501

## PYTEST
- python -m pytest


## INGEST 
- python -m ingestion.ingest_news
- Open DuckDB:
    duckdb world_news.duckdb
    SELECT COUNT(*) FROM articles;
    DESCRIBE articles;
- streamlit run dashboard/app.py

## Normalize the data
Insert into your DuckDB database (world_news.duckdb) After it finishes, the log will say something like Inserted XXX rows into DuckDB.

### DUCKDB
- duckdb world_news.duckdb
- SELECT * FROM articles;
- SELECT country, language FROM articles;

## DAGSTER 
**See data loaded in dagster:**
- dagster dev -f dagster_code/repository.py
- Jobs tab → news_job
- Schedules tab → three_times_a_day_schedule
- Test your job manually
- Click on Jobs → news_job → Launch Run.

## STREAMLIT
- streamlit run dashboard/app.py



