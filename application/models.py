from werkzeug import generate_password_hash, check_password_hash
from application import db
from application import app

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key = True)
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
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user = db.relationship('User', backref='sections')

	def __init__(self, name, user_id):
		self.name = name.title()
		self.user_id = user_id

	def __repr__(self):
		return '<Section %r>' % self.name


class Schedule(db.Model):
	__tablename__ = 'schedule'
	id = db.Column(db.Integer, primary_key = True)
	day = db.Column(db.Integer)
	start_time = db.Column(db.DateTime)
	end_time = db.Column(db.DateTime)
	section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
	section = db.relationship('Section', backref='schedules')

	def __init__(self, *args, **kwargs):
		db.Model.__init__(self, *args, **kwargs)

	def __repr__(self):
		return '<Schedule %r - %r>' % (self.start_time, self.end_time)

class Job(db.Model):
	__tablename__ = 'job'
	id = db.Column(db.Integer, primary_key = True)
	job_id = db.Column(db.Integer)
	schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
	schedule = db.relationship('Schedule', backref='jobs')

	def __init__(self, *args, **kwargs):
		db.Model.__init__(self, *args, **kwargs)

	def __repr__(self):
		return '<Job %s>' % (self.job_id)

class Marker(db.Model):
	__tablename__ = 'marker'
	id = db.Column(db.Integer, primary_key = True)
	timestamp = db.Column(db.DateTime)
	start_time = db.Column(db.DateTime)
	end_time = db.Column(db.DateTime)

	def __repr__(self):
		return '<Marker %r>' % (self.timestamp)


# models for which we want to create API endpoints
app.config['API_MODELS'] = { 
	'section': Section,
	'schedule': Schedule,
	'marker': Marker
	}

