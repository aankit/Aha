from pytz import utc

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

#make sure to add code that sets timezone from database

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite') #replace with postgres
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 3
}

timezone = utc