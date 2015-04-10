from application import app
import sh, time, os

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
	print current_file
	print "------"
	return current_file[0] #only one file can exist here at a time

def record_off():
	sh.touch(app.config["RECORD_PATH"] + '/stop_record')

def record_state():
	curr_recording = sh.ls(app.config["TMP_VIDEO_PATH"]).stdout
	if curr_recording:
		return curr_recording
	else:
		return False

def test():
	pid = service_on()
	time.sleep(2)
	current_file = record_on()
	return pid, current_file
