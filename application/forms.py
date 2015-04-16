from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, IntegerField, HiddenField
from wtforms_components import TimeField
from wtforms import SelectField, validators, widgets, SelectMultipleField
from datetime import timedelta
from application import db
from application.models import *
from application.filters import dayformat
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


class ScheduleForm(Form):
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

    def validate(self, recording_id=None):
        if recording_id is None:
            if not Form.validate(self):
                print "form not validating"
                return False
        #check to see if the start time is greater than end time
        if self.start_time.data > self.end_time.data:
            self.start_time.errors.append("Your start time comes after your end time...")
            return False
        if  self.check_conflicts(recording_id):
            return False
        else:
            return True


    def check_conflicts(self, recording_id):
        #check schedule first for if there is anything on the schedule for the days chosen
        #then if there is start time conflict or an end time conflict
        conflicts = db.session.query(Schedule.day, Schedule.start_time, Section.name) \
            .join(Schedule.section) \
            .filter(Schedule.day.in_(self.days.data)) \
            .filter(
                ((Schedule.start_time <= self.start_time.data) & (Schedule.end_time > self.start_time.data)) |
                ((Schedule.start_time < self.end_time.data) & (Schedule.end_time >= self.end_time.data)))
        if recording_id:
            conflicts = conflicts.filter(Schedule.id != recording_id)
        conflict = conflicts.first()
        if conflict:
            self.start_time.errors.append("One or more of the times you are scheduling conflicts with the %s %s of %s"
                % (dayformat(conflict.day), conflict.start_time, conflict.name))
            return True
        else:
            return False
