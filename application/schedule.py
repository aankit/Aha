from application.models import *
from application import scheduler
from application import picam
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import time

def scheduler_job():
	print "scheduler job working"

def cam_record():
	picam_service = picam.service_on()
	if picam_service:
		recording_filename, command_sent = picam.record_on()
		hms = time.strftime("%H:%M:%S", time.localtime(command_sent))
		day = time.strftime("%w")
		job_time = datetime.strptime("1900-01-01_"+hms, "%Y-%m%d_%H:%M:%S")
		try:
			schedule_obj = db.session.query(Schedule) \
			.filter((Schedule.day==day) & \
				(Schedule.start_time<=job_time) & \
				(Schedule.end_time>=job_time)).one()
		except MultipleResultsFound:
			app.logger.warning("multiple sections found when starting recording")
			raise
		except NoResultFound:
			app.logger.warning("no section found when starting recording")
			raise
		video_obj = Video(filename=recording_filename, start_time=schedule_obj.job_time, section_id=schedule_obj.section_id)
		db.session.add(video_obj)
		db.session.commit()
	else:
		raise Exception("the picam service could not been started")


def cam_off():
	sh.touch('/home/pi/hooks/stop_record')
	sh.sudo('service', 'picam', 'stop')

def add_cron(func, job_id, day, hour, minute): 
	scheduler.add_job(func, "cron", 
		id=job_id,
		day_of_week=day, 
		hour=hour, 
		minute=minute
	)
	return 0

def remove_cron(job_id):
	scheduler.remove_job(job_id)
	return 0

def add_schedule(form, session):
	#make section object 
	section_obj = Section.query.filter_by(name=form.section.data.title()).first()
	if section_obj:
		return 403, "This section already has recordings, check out the schedule."
	else:
		section_obj = Section(name=form.section.data, 
			user_id=db.session.query(User.id).filter_by(email=session['email']).first()[0])
		db.session.add(section_obj)
		db.session.commit()
	#iterate through the days
	for day in form.days.data:
		print day
		try:
			#store the times
			schedule_obj = Schedule(day=day, 
			  start_time=form.start_time.data, 
			  end_time=form.end_time.data, 
			  section_id=section_obj.id)
			print schedule_obj
			db.session.add(schedule_obj)
			db.session.commit()
			#create jobs
			start_job = "%d_start" % (schedule_obj.id)
			end_job = "%d_end" % (schedule_obj.id)
			add_cron(cam_record, start_job, day,form.start_time.data.hour,form.start_time.data.minute)
			add_cron(cam_off, end_job, day,form.end_time.data.hour,form.end_time.data.minute)
			#save job ids in database
			start_obj = Job(job_id=start_job, schedule_id=schedule_obj.id)
			stop_obj = Job(job_id=end_job, schedule_id=schedule_obj.id)
			db.session.add(start_obj)
			db.session.add(stop_obj)
			db.session.commit()
		except Exception as error:
			db.session.rollback()
			return 500, error
		#redirecting back to schedule page with flash for success
	return 201, "Success! You have added a recording."

def edit_schedule(form, session):
	#look up session
	schedule_objs = db.session.query(Schedule) \
		.join(Schedule.section) \
		.filter(Section.name==form.section.data).all()
	print schedule_objs
	if not schedule_objs:
		return 404, "Section not found."
	try:
		for schedule_obj in schedule_objs:
			#modify days already in the database
			if schedule_obj.day in form.days.data:
				schedule_obj.start_time = form.start_time.data
				schedule_obj.end_time = form.end_time.data
			#delete days that the user has not specified in new schedule
			else:
				jobs = schedule_obj.jobs
				for job in jobs:
					remove_cron(job)
				db.session.delete(schedule_obj)
				db.session.commit()
			
		#and add days not in there
		for day in form.days.data:
			print day
			if day not in [schedule_obj.day for schedule_obj in schedule_objs]:
				schedule_obj = Schedule(day=day, 
				  start_time=form.start_time.data,
				  end_time=form.end_time.data,
				  section_id=Section.query.filter_by(name=form.section.data).first().id)
				db.session.add(schedule_obj)
				db.session.commit()

	except Exception as error:
		db.session.rollback()
		return 500, error

	return 201, "Success! You have editing recording for %s" %(form.section.data)

def get_scheduled():
	return db.session.query(Schedule).join(Schedule.section).all()

