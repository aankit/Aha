from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from application.sessions import ItsdangerousSessionInterface as session_interface
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_object('application.settings')
app.url_map.strict_slashes = False
app.session_interface = session_interface()

db = SQLAlchemy(app)
api_manager = APIManager(app, flask_sqlalchemy_db=db)

handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

import application.models
from application.filters import datetimeformat, dayformat

app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['dayformat'] = dayformat

#our routes
import application.controllers
