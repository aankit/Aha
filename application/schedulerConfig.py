import pytz

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

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

<<<<<<< HEAD
timezone = pytz.timezone('US/Eastern') #this should be set by user
=======
timezone = pytz.timezone('US/Eastern')  # this should be set by user
>>>>>>> 01a186655242095437da56df65b530ef8c5aa61f
