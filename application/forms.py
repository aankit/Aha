from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms_components import TimeField
from wtforms import SelectField, validators, widgets, SelectMultipleField
from datetime import timedelta
from application import db
from application.models import *
import pytz


class SettingsForm(Form):
    timezone = SelectField("Timezone",
        [validators.Required("Please select your timezone:")],
        choices=[pytz.all_timezones]
        )
    rubric_url = StringField("Link to Observation Rubric:")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


class SignupForm(Form):
    email = StringField("Email", validators=[validators.Required("Email Address"), validators.Email(message="Invalid Email")])
    password = PasswordField("Password", validators=[validators.Required("Choose a Password")])
    submit = SubmitField("Create account")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user:
            self.email.errors.append("That email is already taken.")
            return False
        else:
            return True


class SigninForm(Form):
    email = StringField("Email",  [validators.Required("Please enter your email address."),
        validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return user
        else:
            self.email.errors.append("Invalid e-mail or password")
            return False


class Student(Form):
    nickname = StringField("Name/Nickname", [validators.Required("Please enter a name for the student")])
    category = StringField("Category", [validators.Required("Please ")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


class LessonSegment(Form):
    name = StringField("Segment Name", [validators.Required("What do you want to call this segment")])
    start_time = IntegerField("How many minutes into the lesson do you intend on starting?",
        [validators.Required("Please enter when the segment starts.")])
    end_time = IntegerField("When do you intend of ending?", [validators.Required("Please enter when the segment ends")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


class LessonPlan(Form):
    section = SelectField("Choose a section:",
        [validators.Required("Please choose a section.")],
        coerce=int)

    def __init__(self, *args, **kwargs):
            Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False


class SectionForm(Form):
    name = StringField("Section/Class Name", [validators.Required("Please enter a section/class name")])
    # submit = SubmitField("Add Section")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self, user_id):
        if not Form.validate(self):
            return False

        section = Section.query.filter_by(user_id=user_id, name=self.name.data.title()).first()
        if section:
            self.name.errors.append("That section name is already taken.")
            return False
        else:
            return True


class newScheduleForm(Form):
    days = SelectMultipleField("Choose day(s) for recording?",
        [validators.Required("Please enter the day(s)")],
        choices=[(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday")],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        coerce=int)
    start_time = TimeField("Start Time",[validators.Required("What time should recording start?")])
    end_time = TimeField("End Time",[validators.Required("What time should recording end?")])
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        else:
            return True

    def get_data(self, recording_id):
        schedule_objs = db.session.query(Schedule).filter_by(recording_id=recording_id).all()
        d = dict()
        if schedule_objs:
            d['days'] = [schedule_obj.day for schedule_obj in schedule_objs]
            d['start_time'] = self.toggleTime(schedule_objs[0].start_time)
            d['end_time'] = self.toggleTime(schedule_objs[0].end_time)
        return d


class ScheduleForm(Form):
    section = SelectField("Choose a section:",
        [validators.Required("Please choose a section.")],
        coerce=int)

    days = SelectMultipleField("What days do you see them?",
        [validators.Required("Please enter the days you teach this class")],
        choices=[(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday")],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        coerce=int)
    #start time, separating AM and PM because of date formatting issues with %p, good place to optimize later
    start_time = TimeField("Start Time",
        [validators.Required("What time does class start?")])
    start_ampm = SelectField("AM/PM",
        [validators.Required("Please select AM/PM for start time")], 
        choices=[("AM", "AM"), ("PM", "PM")])

    #end time, same deal as start time
    end_time = TimeField("End Time",
        [validators.Required("What time does class end?")])
    end_ampm = SelectField("AM/PM",
        [validators.Required("Please select AM/PM for end time")], 
        choices=[("AM", "AM"), ("PM", "PM")])

    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        else:
            #convert time to 24 hour format
            self.start_time.data = self.toggleTime(self.start_time.data, self.start_ampm.data)
            self.end_time.data = self.toggleTime(self.end_time.data, self.end_ampm.data)

            #check to see if the start time is greater than end time
            if self.start_time.data > self.end_time.data:
                self.start_time.errors.append("Your start time comes after your end time...")
                return False
            #check schedule first for if there is anything on the schedule for the days chosen
            #then if there is start time conflict or an end time conflict
            conflict = db.session.query(Schedule.start_time, Section.name) \
                .join(Schedule.section) \
                .filter(Schedule.day.in_(self.days.data)) \
                .filter(((Schedule.start_time <= self.start_time.data) & (Schedule.end_time > self.start_time.data)) |
                ((Schedule.start_time < self.end_time.data) & (Schedule.end_time >= self.end_time.data))).all()

            if conflict:
                self.days.errors.append("One or more of the times you are scheduling conflicts with this %r" % (conflict))
                return False
            else:
                return True

    def populate_section(self, user_id):
        self.section.choices = db.session.query(Section.id, Section.name).filter_by(user_id=user_id).all()

    def get_data(self, id):
        section_id = db.session.query(Schedule.section_id).filter_by(id=id).one()
        schedule_objs = db.session.query(Schedule) \
            .join(Schedule.section) \
            .filter(Section.id == section_id[0]).all()
        d = dict()
        if schedule_objs:
            d['days'] = [schedule_obj.day for schedule_obj in schedule_objs]
            d['section'] = schedule_objs[0].section.name
            d['start_time'] = self.toggleTime(schedule_objs[0].start_time)
            d['start_ampm'] = self.getAMPM(schedule_objs[0].start_time)
            d['end_time'] = self.toggleTime(schedule_objs[0].end_time)
            d['end_ampm'] = self.getAMPM(schedule_objs[0].end_time)
        return d

    def toggleTime(self, time, ampm=None):
        if time.hour > 12:
            return time - timedelta(hours=12)
        elif ampm == 'PM':
            return time + timedelta(hours=12)
        else:
            return time

    def getAMPM(self, time):
        if time.hour > 12:
            return 'PM'
        else:
            return 'AM'