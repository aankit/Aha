from werkzeug import generate_password_hash, check_password_hash
from application.core import db
from application import app

class User(db.Model):
	__tablename__ = 'user'
	uid = db.Column(db.Integer, primary_key = True)
	firstname = db.Column(db.String(100))
	lastname = db.Column(db.String(100))
	email = db.Column(db.String(120), unique=True)
	pwdhash = db.Column(db.String(54))

	def __init__(self, firstname, lastname, email, password):
		self.firstname = firstname.title()
		self.lastname = lastname.title()
		self.email = email.lower()
		self.set_password(password)
	 
	def set_password(self, password):
		self.pwdhash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.pwdhash, password)

	def __repr__(self):
		return '<User %r>' % self.email

class Section(db.Model):
	__tablename__ = 'section'
	uid = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))

	def __init__(self, name):
		self.name = name.title()

	def __repr__(self):
		return '<Section %r>' % self.name

class Schedule(db.Model):
	__tablename__ = 'schedule'
	uid = db.Column(db.Integer, primary_key = True)
	day = db.Column(db.Integer)
	start_time = db.Column(db.DateTime)
	end_time = db.Column(db.DateTime)
	section_id = db.Column(db.Integer, db.ForeignKey('section.uid'))
	section = db.relationship('Section', backref='schedule')

	def __init__(self, start, end, section_id):
		self.start = start
		self.end = end
		self.section_id = section_id

	def __repr__(self):
		return '<Schedule %r>' % (self.datetime)

# models for which we want to create API endpoints
app.config['API_MODELS'] = { 'user': User, }

# models for which we want to create CRUD-style URL endpoints,
# and pass the routing onto our AngularJS application
app.config['CRUD_URL_MODELS'] = { 'user': User }