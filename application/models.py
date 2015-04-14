from sqlalchemy.dialects import postgresql
from werkzeug import generate_password_hash, check_password_hash
from application import db
from application import app


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(100))
    timezone = db.String(db.String(15))
    rubric_url = db.String(db.String(200))

    def __init__(self, email, password):
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
    id = db.Column(db.Integer, primary_key=True)
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
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer)
    start_time = db.Column(postgresql.TIME())  # these times all happen on January 1st, 1900
    end_time = db.Column(postgresql.TIME())    # since I don't care about dates for recurring scheduling
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    section = db.relationship('Section', backref='schedule')

    def __init__(self, *args, **kwargs):
        db.Model.__init__(self, *args, **kwargs)

    def __repr__(self):
        return '<Schedule %r - %r>' % (self.start_time, self.end_time)


class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    schedule = db.relationship('Schedule', backref='jobs')

    def __init__(self, *args, **kwargs):
        db.Model.__init__(self, *args, **kwargs)

    def __repr__(self):
        return '<Job %s>' % (self.job_id)


class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(25))
    start_time = db.Column(db.DateTime)  # this is an actual time!
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    schedule = db.relationship('Schedule', backref='videos')

    def __repr__(self):
        return '<Video %s>' % (self.filename)


class Marker(db.Model):
    __tablename__ = 'marker'
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Marker %r>' % (self.timestamp)


# models for which we want to create API endpoints
app.config['API_MODELS'] = {
    'section': Section,
    'schedule': Schedule,
    'video': Video,
    'marker': Marker
    }
