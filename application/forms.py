from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, DateTimeField
from wtforms import SelectField, validators, widgets, SelectMultipleField
from application import db
from models import User, Section, Schedule
from datetime import timedelta

class SignupForm(Form):
	firstname = StringField("First Name", validators=[validators.Required("First Name")])
	lastname = StringField("Last Name", validators=[validators.Required("Last Name")])
	email = StringField("Email", validators=[validators.Required("Email Address")])
	password = PasswordField("Password", validators=[validators.Required("Choose a Password")])
	submit = SubmitField("Create account")

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False

		user = User.query.filter_by(email = self.email.data.lower()).first()
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
	 
		user = User.query.filter_by(email = self.email.data.lower()).first()
		if user and user.check_password(self.password.data):
		  return True
		else:
		  self.email.errors.append("Invalid e-mail or password")
		  return False


class ScheduleForm(Form):
	section = StringField("What section/class will you be teaching?", 
		[validators.Required("Please enter the class/section name.")])
	
	days = SelectMultipleField("What days do you see them?", 
		[validators.Required("Please enter the days you teach this class")], 
		choices=[(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday")],
		option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        coerce=int
        )
	#start time, separating AM and PM because of date formatting issues with %p, good place to optimize later
	start_time = DateTimeField("Start Time", 
		[validators.Required("What time does class start?")],
		format = '%I:%M'
		)
	start_ampm = SelectField("AM/PM", 
		[validators.Required("Please select AM/PM for start time")], 
		choices=[("AM", "AM"), ("PM", "PM")])
	
	#end time, same deal as start time
	end_time = DateTimeField("End Time", 
		[validators.Required("What time does class end?")],
		format = '%I:%M'
		)
	end_ampm = SelectField("AM/PM", 
		[validators.Required("Please select AM/PM for end time")], 
		choices=[("AM", "AM"), ("PM", "PM")])
	
	submit = SubmitField("Add to Schedule")
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False
		else:
			self.start_time.data = self.start_time.data + timedelta(hours=12) if self.start_ampm.data=='PM' else self.start_time.data
			self.end_time.data = self.end_time.data + timedelta(hours=12) if self.end_ampm.data=='PM' else self.end_time.data
			if self.start_time.data > self.end_time.data:
				self.start_time.errors.append("Your start time comes after your end time...")
				return False
			#check schedule first for if there is anything on the schedule for the days chosen
			#then if there is start time conflict or an end time conflict
			conflicts = db.session.query(Schedule.start_time, Section.name) \
				.join(Schedule.section) \
				.filter(Schedule.day.in_(self.days.data)) \
				.filter(((Schedule.start_time<=self.start_time.data) & (Schedule.end_time>self.start_time.data)) | \
				((Schedule.start_time<self.end_time.data) & (Schedule.end_time>=self.end_time.data))).all()

			if conflicts:
				self.days.errors.append("One or more of the times you are scheduling conflicts with this %r" %(conflicts))
				return False
			else:
				return True














