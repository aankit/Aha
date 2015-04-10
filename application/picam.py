from application import app
import sh, os

def service_on():
	sh.sudo('service','picam', 'start')
	pid = service_state()
	return pid

def service_off():
	sh.sudo('service', 'picam', 'stop')

def service_state():
	try:
		pid = sh.pidof('picam')
		return pid 
	except:
		return False

def record_on():
	sh.touch(app.config["RECORD_PATH"] + '/start_record')
	current_file = os.listdir(app.config["TMP_VIDEO_PATH"])
	while len(current_file)==0:
		current_file = os.listdir(app.config["TMP_VIDEO_PATH"])
	return current_file[0] #only one file can exist here at a time

def record_off():
	sh.touch(app.config["RECORD_PATH"] + '/stop_record')

def record_state():
	current_file = os.listdir(app.config["TMP_VIDEO_PATH"])
	if current_file:
		return current_file[0]
	else:
		return False
