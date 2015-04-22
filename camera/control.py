import settings
import sh
import os
import time


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
    while record_state() == 'off':
        check = time.time()
        if check - now > 0.5:
            sh.touch(settings.ONOFF_PATH + '/start_record')
            now = check
    return record_file()


def record_off():
    filename = record_file()
    sh.touch(settings.ONOFF_PATH + '/stop_record')
    while record_state() == 'on':
        continue
    return filename


def record_state():
    current_file = os.listdir(settings.CURRENT_RECORDING_PATH)
    if current_file:
        return 'on'
    else:
        return 'off'


def record_file():
    current_file = os.listdir(settings.CURRENT_RECORDING_PATH)
    if current_file:
        return current_file[0]
    else:
        False


def record_refresh():
    if record_state() == 'on':
        record_off()
        record_on()
        return True
    else:
        return False


def get_all_recordings():
    return [settings.ARCHIVE_RECORDING_PATH+'/'+filename for filename in os.listdir(settings.ARCHIVE_RECORDING_PATH)]


def get_recording(file_list_index=0, full_path=False):
    sorted_filenames_with_path = sorted(get_all_recordings(), key=os.path.getctime, reverse=True)
    return_list = []
    if full_path:
        return_list = sorted_filenames_with_path
    else:
        sorted_filenames = [filename.split('/')[-1] for filename in sorted_filenames_with_path]
        return_list = sorted_filenames
    try:
        get_file = return_list[file_list_index]
    except:
        get_file = None
    return get_file


def remove_recording(file_list_index=0):
    recording = get_recording(file_list_index, full_path=True)
    os.remove(recording)
    print "removed: %s" % (recording)


def clean_archive():
    for recording in get_all_recordings():
        os.remove(recording)
        print "removed: %s" % (recording)


def get_log_file():
    return settings.LOG_FILE
