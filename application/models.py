from sqlalchemy.dialects import postgresql
from werkzeug import generate_password_hash, check_password_hash
from application import db
from application import app

#secondary tables
conjectures = db.Table('conjecture_investigation',
                       db.Column('conjecture_id',
                                 db.Integer,
                                 db.ForeignKey('conjecture.id'),
                                 nullable=False),
                       db.Column('investigation_id',
                                 db.Integer,
                                 db.ForeignKey('investigation.id'),
                                 nullable=False))

schedule_videos = db.Table('schedule_video',
                           db.Column('schedule_id',
                                     db.Integer,
                                     db.ForeignKey('schedule.id'),
                                     nullable=False),
                           db.Column('video_id',
                                     db.Integer,
                                     db.ForeignKey('video.id'),
                                     nullable=False))

marker_videos = db.Table('marker_video',
                         db.Column('marker_id',
                                   db.Integer,
                                   db.ForeignKey('marker.id'),
                                   nullable=False),
                         db.Column('video_id',
                                   db.Integer,
                                   db.ForeignKey('video.id'),
                                   nullable=False))


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


class Investigation(db.Model):
    __tablename__ = 'investigation'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(140))
    start_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='investigations')

    def __init__(self, question, user_id):
        self.question = question.capitalize()
        self.user_id = user_id

    def __repr__(self):
        return '<Investigation %r>' % self.question


class Conjecture(db.Model):
    __tablename__ = 'conjecture'
    id = db.Column(db.Integer, primary_key=True)
    conjecture = db.Column(db.String(140))
    commentary = db.Column(db.Text)
    investigations = db.relationship('Investigation',
                                     backref=db.backref('conjectures', lazy='dynamic'),
                                     secondary=conjectures)

    def __repr__(self):
        return '<Conjecture %r>' % self.conjecture


class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(25))
    date = db.Column(db.Date)
    start_time = db.Column(postgresql.TIME())  # this is an actual time!
    end_time = db.Column(postgresql.TIME())

    def __repr__(self):
        return '<Video %s>' % (self.filename)


class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date())
    day = db.Column(db.Integer)
    start_time = db.Column(postgresql.TIME())
    end_time = db.Column(postgresql.TIME())
    investigation_id = db.Column(db.Integer, db.ForeignKey('investigation.id'))
    investigation = db.relationship('Investigation', backref='schedule')
    videos = db.relationship('Video', backref=db.backref('schedules', lazy='dynamic'),
                             secondary=schedule_videos)

    def __repr__(self):
        return '<Schedule %r - %r>' % (self.start_time, self.end_time)


class Marker(db.Model):
    __tablename__ = 'marker'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    day = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    videos = db.relationship('Video', backref=db.backref('markers', lazy='dynamic'),
                             secondary=marker_videos)

    def __repr__(self):
        return '<Marker %r>' % (self.timestamp)


# models for which we want to create API endpoints
app.config['API_MODELS'] = {
    'investigation': Investigation,
    'conjecture': Conjecture,
    'schedule': Schedule,
    'video': Video,
    'marker': Marker
    }
