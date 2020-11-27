"""This module is the execution entry point for the Data Mart Refresher (DMR).

It starts periodic CRON jobs to trigger DWH data mart updates. Beyond that, two jobs send notifications
to the external Model Training Service (MTS) and Image Labelling Service (ILS).

The latter mechanisms either tell the respective service which city
model to create/update (MTS) or whose city's images to label (ILS).
"""
from cron_jobs.jobs import trigger_data_marts_refresh, trigger_city_model_training, trigger_city_image_labelling
from os import environ
from time import sleep
from cron_jobs.jobs import start_cron_job
import schedule

# read endpoint URLs of external services from environment variables
REFRESH_DATA_MARTS_EVERY_SECONDS = int(environ['REFRESH_DATA_MARTS_EVERY_SECONDS'])
ENABLE_MODEL_TRAINING_EVERY_SECONDS = int(environ['ENABLE_MODEL_TRAINING_EVERY_SECONDS'])
ENABLE_LABELLING_REQUESTS_EVERY_SECONDS = int(environ['ENABLE_LABELLING_REQUESTS_EVERY_SECONDS'])
SAFE_DELAY_IN_SECONDS = 1  # generously account for internal scheduling tasks


start_cron_job(trigger_data_marts_refresh, REFRESH_DATA_MARTS_EVERY_SECONDS)
start_cron_job(trigger_city_model_training, ENABLE_MODEL_TRAINING_EVERY_SECONDS)
start_cron_job(trigger_city_image_labelling, ENABLE_LABELLING_REQUESTS_EVERY_SECONDS)


while True:
    schedule.run_pending()
    sleep(SAFE_DELAY_IN_SECONDS)
