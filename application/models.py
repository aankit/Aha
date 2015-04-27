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

markers = db.Table('investigation_markers',
                   db.Column('investigation_id',
                             db.Integer,
                             db.ForeignKey('investigation.id'),
                             nullable=False),
                   db.Column('marker_id',
                             db.Integer,
                             db.ForeignKey('marker.id'),
                             nullable=False))

schedule_videos = db.Table('schedule_videos',
                           db.Column('schedule_id',
                                     db.Integer,
                                     db.ForeignKey('schedule.id'),
                                     nullable=False),
                           db.Column('video_id',
                                     db.Integer,
                                     db.ForeignKey('video.id'),
                                     nullable=False))

marker_videos = db.Table('marker_videos',
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
    media_url = db.Column(db.String(200))

    def __init__(self, email, password, media_url=app.config["MEDIA_DIR"]):
        self.email = email.lower()
        self.set_password(password)
        self.media_url = media_url

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
    filepath = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='investigations')
    conjectures = db.relationship('Conjecture',
                                  backref=db.backref('investigations', lazy='dynamic'),
                                  secondary=conjectures)
    markers = db.relationship('Marker',
                              backref=db.backref('investigations', lazy='dynamic'),
                              secondary=markers)

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

    def __repr__(self):
        return '<Conjecture %r>' % self.conjecture


class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    media_path = db.Column(db.String(25))
    date = db.Column(db.Date)

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
    date = db.Column(db.Date)
    start_time = db.Column(postgresql.TIME())
    end_time = db.Column(postgresql.TIME())
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
