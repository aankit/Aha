from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from application.sessions import ItsdangerousSessionInterface as session_interface
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager

app = Flask(__name__)
app.config.from_object('application.settings')
app.url_map.strict_slashes = False
app.session_interface = session_interface()

db = SQLAlchemy(app)
api_manager = APIManager(app, flask_sqlalchemy_db=db)
import application.models

from application.schedulerConfig import jobstores, executors, job_defaults, timezone
scheduler = BackgroundScheduler(jobstores=jobstores, 
	executors=executors, 
	job_defaults=job_defaults, 
	timezone=timezone)

scheduler.start()
print 'scheduler started'

#our routes
import application.controllers
import application.schedule