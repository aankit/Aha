from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, DateTimeField
from wtforms import SelectField, validators, widgets, SelectMultipleField
from datetime import timedelta
from application import db
from models import User, Section, Schedule


class SignupForm(Form):
	firstname = StringField("First Name", validators=[validators.Required("First Name")])
	lastname = StringField("Last Name", validators=[validators.Required("Last Name")])
	email = StringField("Email", validators=[validators.Required("Email Address"), validators.Email(message="Invalid Email")])
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
        coerce=int,
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

	def get_data(self, id):
		schedule_objs = db.session.query(Schedule) \
			.join(Schedule.section) \
			.filter(Section.id==id).all()
		d = dict()
		if schedule_objs:
			d['days'] = [schedule_obj.day for schedule_obj in schedule_objs]
			d['section'] = schedule_objs[0].name
			d['start_time'] = self.toggleTime(schedule_objs[0].start_time)
			d['start_ampm'] = self.getAMPM(schedule_objs[0].start_time)
			d['end_time'] = self.toggleTime(schedule_objs[0].end_time)
			d['end_ampm'] = self.getAMPM(schedule_objs[0].end_time)
		return d


	def toggleTime(self,time, ampm=None):
		if time.hour > 12:
			return time - timedelta(hours=12) 
		elif ampm == 'PM':
			return time + timedelta(hours=12) 
		else:
			return time

	def getAMPM(self,time):
		if time.hour > 12:
			return 'PM'
		else:
			return 'AM'

class Timezone(Form):
	timezone = SelectField("Timezone",
		[validators.Required("Please select your timezone")],
		choices = ['US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific']
		)

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False















