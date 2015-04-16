import pytz

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.events import *
from application.schedule import process_video

#make sure to add code that sets timezone from database

jobstores = {
        'default': SQLAlchemyJobStore(url='postgresql+psycopg2://aha:aha@/aha') #replace with postgres
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 3,
    'misfire_grace_time': 10

}

timezone = pytz.timezone('US/Eastern') #this should be set by user

scheduler = BackgroundScheduler(jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=timezone)

scheduler.add_listener(process_video, EVENT_JOB_EXCUTED | EVENT_JOB_ERROR)