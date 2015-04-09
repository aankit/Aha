from application import app
import sh, time, os

def service_on():
	sh.sudo('service','picam', 'start')
	pid = sh.pidof('picam')
	command_sent = time.time()
	current_time = time.time()
	while not pid:
		pid = sh.pidof('picam')
		current_time = time.time()
		if command_sent - current_time > 20:
			app.logger.warning("picam service on timed out")
			break;
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
	videos = os.listdir(app.config["VIDEO_PATH"])
	video_times = [os.path.getctime(app.config["VIDEO_PATH"] + '/' + video) for video in videos]
	current_file = videos[video_times.index(min(video_times))]
	return current_file

def record_off():
	sh.touch(app.config["RECORD_PATH"] + '/stop_record')

def record_state():
	curr_recording = sh.ls(app.config["TMP_VIDEO_PATH"]).stdout
	if curr_recording:
		return curr_recording
	else:
		return False



