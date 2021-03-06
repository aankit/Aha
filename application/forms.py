from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, IntegerField, HiddenField, TextAreaField
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


class InvestigationForm(Form):
    question = TextAreaField("Ask a question about your practice or classroom.",
                             [validators.Required("Please enter an investigation question."),
                              validators.length(max=140)])
    # submit = SubmitField("Add Section")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self, user_id):
        if not Form.validate(self):
            return False

        investigation = Investigation.query.filter_by(user_id=user_id, question=self.question.data.capitalize()).first()
        if investigation:
            self.question.errors.append("You already asked that question, find it or ask another.")
            return False
        else:
            return True


class ScheduleForm(Form):
    days = SelectMultipleField("Choose day(s) for recording?",
                               [validators.Required("Please enter the day(s)")],
                               choices=[(0, "Monday"),
                                        (1, "Tuesday"),
                                        (2, "Wednesday"),
                                        (3, "Thursday"),
                                        (4, "Friday")],
                               option_widget=widgets.CheckboxInput(),
                               widget=widgets.ListWidget(prefix_label=False),
                               coerce=int)
    start_time = TimeField("Start Time", [validators.Required("What time should recording start?")])
    end_time = TimeField("End Time", [validators.Required("What time should recording end?")])
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
        else:
            return True
        # if  self.check_conflicts(recording_id):
        #     return False
        # else:
        #     return True


    # def check_conflicts(self, recording_id):
    #     #check schedule first for if there is anything on the schedule for the days chosen
    #     #then if there is start time conflict or an end time conflict
    #     conflicts = db.session.query(Schedule.day, Schedule.start_time, Section.name) \
    #         .join(Schedule.section) \
    #         .filter(Schedule.day.in_(self.days.data)) \
    #         .filter(
    #             ((Schedule.start_time <= self.start_time.data) & (Schedule.end_time > self.start_time.data)) |
    #             ((Schedule.start_time < self.end_time.data) & (Schedule.end_time >= self.end_time.data)))
    #     if recording_id:
    #         conflicts = conflicts.filter(Schedule.id != recording_id)
    #     conflict = conflicts.first()
    #     if conflict:
    #         self.start_time.errors = list(self.start_time.errors)  
    #         # this is a hack, not sure why the Form.validate wasn't validating so I removed it and need to list() it
    #         self.start_time.errors.append("One or more of the times you are scheduling conflicts with the %s %s of %s"
    #             % (dayformat(conflict.day), conflict.start_time, conflict.name))
    #         return True
    #     else:
    #         return False
