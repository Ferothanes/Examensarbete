# Examensarbete

APIs → Docker Postgres → Transform → Dagster → Taipy dashboard

docker ps
docker exec -it world_news_db psql -U user -d world_news --> test connection to host and postgressql

using pgAdmin (Web GUI for Postgres) to visualize my ingestions and changes
- The standard visual interface for PostgreSQL.
- You can run queries, see tables, inspect rows, add new tables, etc.
- add pgAdmin in your docker-compose
- Go to http://localhost:8080. Log in with credentials from docker-compose.yml

---
### PORTS:
- world_news_db (Postgres) → 5432
- pgAdmin → 8080
---

# API
1️⃣ NewsAPI.org

Why it’s good for the project:

Wide coverage: Aggregates news from thousands of media outlets worldwide.

Easy to filter: Country, language, category (sports, technology, business, etc.) — fits your dashboard idea perfectly.

REST API: Easy to integrate with Python requests or any ETL tool.

Free tier available: Good for development/testing (up to 100 requests/day).

Structured JSON output: Makes normalization and storage straightforward.

Potential limitation: Free tier is limited in volume and rate; may need multiple API keys for heavy usage.

## INGESTION

run - python ingest/ingest_news.py



## DAGSTER
dagit -f dagster/repository.py 
Open http://localhost:3000


