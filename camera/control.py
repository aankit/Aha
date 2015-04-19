from camera import settings
import sh
import os
from time


def service_on():
    sh.sudo('service', settings.CAMERA, 'start')
    pid = service_state()
    return pid


def service_off():
    sh.sudo('service', settings.CAMERA, 'stop')


def service_state():
    try:
        pid = sh.pidof(settings.CAMERA)
        return pid.stdout[:-1]
    except:
        return False


def service_refresh():
    service_off()
    service_on()


def record_on():
    sh.touch(settings.ONOFF_PATH + '/start_record')
    now = time.time()
    while not record_state():
        print "starting"
        check = time.time()
        if check-now > 0.5:
            sh.touch(settings.ONOFF_PATH + '/start_record')
            now = check
    current_file = os.listdir(settings.CURRENT_RECORDING_PATH)
    return current_file[0]  # only one file can exist here at a time


def record_off():
    sh.touch(settings.ONOFF_PATH + '/stop_record')
    while record_state():
        print "stopping"
    return "off"


def record_state():
    current_file = os.listdir(settings.CURRENT_RECORDING_PATH)
    if current_file:
        return current_file[0]
    else:
        return False


def record_refresh():
    current_file = record_state()
    if current_file:
        record_off()
        # sleep(1)
        new_file = record_on()
        return new_file
    else:
        return "nothing recording"


def get_all_recordings():
    return [settings.ARCHIVE_RECORDING_PATH+'/'+filename for filename in os.listdir(settings.ARCHIVE_RECORDING_PATH)]


def get_recording(file_list_index=0):
    return sorted(get_all_recordings(), key=os.path.getctime, reverse=True)[file_list_index]


def clean_archive():
    for recording in get_all_recordings():
        os.remove(recording)
        print "removed: %s" % (recording)
