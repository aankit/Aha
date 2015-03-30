from application import scheduler

# @scheduler.scheduled_job('interval', 
# 	seconds=3,
# 	id = "scheduled_job",
# 	replace_existing=True)
# def timed_job():
# 	print "decorator job working."

def scheduler_job():
	print "scheduler job working"

def cam_start():
	print "camera started"

def cam_stop():
	print "camera stopped"

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
