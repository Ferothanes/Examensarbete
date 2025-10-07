from dagster import job, op
from ingest.ingest_news import ingest_all_apis  # a function calling all APIs and saving to Postgres
#Single entry point for all API ingestion
#Makes Dagster @op simple: just call ingest_all_apis()

@op
def fetch_and_store():
    count = ingest_all_apis()
    return count

@job
def news_job():
    fetch_and_store()
