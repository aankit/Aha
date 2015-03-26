from application import scheduler

# @scheduler.scheduled_job('interval', 
# 	seconds=3,
# 	id = "scheduled_job",
# 	replace_existing=True)
# def timed_job():
# 	print "decorator job working."

def scheduler_job():
	print "scheduler job working"

