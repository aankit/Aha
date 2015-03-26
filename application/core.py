from application import app
from application import db
from flask.ext.restless import APIManager
from application.sessions import ItsdangerousSessionInterface as session_interface

api_manager = APIManager(app, flask_sqlalchemy_db=db)

app.session_interface = session_interface()