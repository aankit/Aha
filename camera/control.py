import settings
import sh
import os
import time
from datetime import datetime


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
    return datetime.now()


def record_state():
    current_file = os.listdir(settings.CURRENT_RECORDING_PATH)
    if current_file:
        return current_file[0]
    else:
        return False


def record_refresh():
    current_file = record_state()
    if current_file:
        prev_end = record_off()
        new_file = record_on()
        return new_file, prev_end
    else:
        return None, None


def get_all_recordings():
    return [settings.ARCHIVE_RECORDING_PATH+'/'+filename for filename in os.listdir(settings.ARCHIVE_RECORDING_PATH)]


def get_recording(file_list_index=0, full_path=False):
    sorted_filenames_with_path = sorted(get_all_recordings(), key=os.path.getctime, reverse=True)
    if full_path:
        return sorted_filenames_with_path
    else:
        sorted_filenames = [filename.split('/')[-1] for filename in sorted_filenames_with_path]
        get_file = sorted_filenames[file_list_index]
        return get_file


def remove_recording(file_list_index=0):
    recording = get_recording(file_list_index)
    os.remove(recording)
    print "removed: %s" % (recording)


def clean_archive():
    for recording in get_all_recordings():
        os.remove(recording)
        print "removed: %s" % (recording)


def get_log_file():
    return settings.LOG_FILE
