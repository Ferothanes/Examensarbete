# dagster/repository.py
from dagster import Definitions
from dagster.jobs import news_job
from dagster.schedules import three_times_a_day_schedule

defs = Definitions(
    jobs=[news_job],
    schedules=[three_times_a_day_schedule],
)
