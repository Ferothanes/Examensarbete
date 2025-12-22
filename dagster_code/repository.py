from dagster import job, op, schedule, Definitions
from ingestion.ingest_news import ingest_all_apis # a function calling all APIs and saving to Postgres
#Single entry point for all API ingestion

@op
def fetch_and_store():
    count = ingest_all_apis()
    return count

@job
def news_job():
    fetch_and_store()

# Calls 3 times a day at 08:00, 12:00, and 16:00 UTC. Mediastack has a limit of 4 times a day on free plan.
@schedule(cron_schedule="0 8,12,16 * * *", job=news_job, execution_timezone="UTC")
def three_times_a_day_schedule():
    return {}

defs = Definitions(
    jobs=[news_job],
    schedules=[three_times_a_day_schedule],
)
