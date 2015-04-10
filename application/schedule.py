from application.models import *
from application import scheduler
from application import picam

def scheduler_job():
	print "scheduler job working"

def cam_record(section_id, start_time=None):
	'''Turns the picam service on if not on,
	starts recording if not already recording,
	and saves the new video'''
	if start_time == None:
		start_time = datetime.now()
	picam_pid = picam.service_state()
	recording_filename = picam.record_state()
	if not picam_pid:
		picam.service_on()
	if not recording_filename:
		recording_filename = picam.record_on()
		video_obj = Video(filename=recording_filename, 
			start_time = start_time, 
			section_id = section_id)
		db.session.add(video_obj)
		db.session.commit()
		video_id = video_obj.id
	return video_id

def cam_off():
	'''Turns the current picam recording off if recording,
	turns the picam service_off if on'''
	picam_pid = picam.service_state()
	recording_filename = picam.record_state()
	if recording_filename:
		picam.record_off()
	if picam_pid:
		picam.service_off()
	return 0

def add_section(form, session):
	'''Need to refactor, the section validation should happen
	at the form level. New recording and edit recording forms
	need different validation'''
	section_name = Section.query.filter(Section.name==form.section.data.title()).all()
	if section_name:
		return False
	#make section object 
	section_obj = Section(name=form.section.data, 
		user_id=db.session.query(User.id).filter_by(email=session['email']).first()[0])
	db.session.add(section_obj)
	db.session.commit()
	return section_obj.id

def add_schedule(form, day, section_id):
	#store the times
	schedule_obj = Schedule(day=day, 
	  start_time=form.start_time.data, 
	  end_time=form.end_time.data, 
	  section_id=section_id)
	db.session.add(schedule_obj)
	db.session.commit()
	#create job ids
	start_job_id = "%d_start" % (schedule_obj.id)
	end_job_id = "%d_end" % (schedule_obj.id)
	#create cron jobs
	scheduler.add_job(cam_record, "cron", 
		kwargs={"section_id":schedule_obj.section_id, "start_time":schedule_obj.start_time},
		id=start_job_id,
		day_of_week=day, 
		hour=form.start_time.data.hour, 
		minute=form.start_time.data.minute
	)
	scheduler.add_job(cam_off, "cron", 
		id=end_job_id, 
		day_of_week=day, 
		hour=form.end_time.data.hour, 
		minute=form.end_time.data.minute
		)
	#save job ids in database
	start_obj = Job(job_id=start_job_id, schedule_id=schedule_obj.id)
	stop_obj = Job(job_id=end_job_id, schedule_id=schedule_obj.id)
	db.session.add(start_obj)
	db.session.add(stop_obj)
	db.session.commit()

def delete_schedule(schedule_id):
	schedule_obj = db.session.query(Schedule).filter_by(id=schedule_id).one()
	name = schedule_obj.section.name
	day = schedule_obj.day
	jobs = schedule_obj.jobs
	db.session.delete(schedule_obj)
	db.session.commit()
	for job in jobs:
		try:
			db.session.delete(job)
			scheduler.remove_job(job.job_id)
		except:
			print 'no job' #can get rid of this later
	return day, name

def edit_schedule(form, section_id):
	#look up schedule objs
	schedule_objs = db.session.query(Schedule).filter(section_id==section_id).all()
	try:
		#modify days already in the database
		for schedule_obj in schedule_objs:
			if schedule_obj.day in form.days.data:
				schedule_obj.start_time = form.start_time.data
				schedule_obj.end_time = form.end_time.data
			#delete days that the user has not specified in new schedule
			else:
				jobs = schedule_obj.jobs
				for job in jobs:
					remove_cron(job.job_id)
				db.session.delete(schedule_obj)
				db.session.commit()		
		#and add days not in there
		for day in form.days.data:
			if day not in [schedule_obj.day for schedule_obj in schedule_objs]:
				add_schedule(form, day, section_id)
	except Exception as error:
		db.session.rollback()
		return 500, error
	return 201, "Success! You have editing recording for %s" %(form.section.data)

def get_scheduled():
	return db.session.query(Schedule).all()

