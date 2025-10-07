from dagster import schedule
from dagster.jobs import news_job

@schedule(cron_schedule="0 8,12,16 * * *", job=news_job, execution_timezone="UTC")
def three_times_a_day_schedule():
    return {}
