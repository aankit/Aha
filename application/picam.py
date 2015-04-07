from application import app
import sh, time, os

def service_on():
	try:
		pid = sh.pidof('picam')
		return pid
	except:
		sh.sudo('service','picam', 'start')
		pid = sh.pidof('picam')
		command_sent = time.time()
		current_time = time.time()
		while not pid:
			pid = sh.pidof('picam')
			current_time = time.time()
			if command_sent - current_time > 20:
				break;
	return pid, command_sent if pid else False

def record_on():
	sh.touch(app.config["RECORD_PATH"] + '/start_record')
	video_path = app.config["VIDEO_PATH"]
	videos = os.listdir('/home/pi/picam/rec/archive')
	video_times = [os.path.getctime(video_path + '/' + video) for video in videos]
	current_file = videos[video_times.index(min(video_times))]
	return current_file

def record_off():
	sh.touch(app.config["RECORD_PATH"] + '/stop_record')

def service_off():
	sh.sudo('service', 'picam', 'stop')