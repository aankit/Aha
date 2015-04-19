from camera import settings
import sh
import os
from time import sleep


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


def record_on():
    sh.touch(settings.ONOFF_PATH + '/start_record')
    current_file = os.listdir(settings.CURRENT_RECORDING_PATH)
    # while len(current_file) == 0:
    #     current_file = os.listdir(settings.CURRENT_RECORDING_PATH)
    return current_file[0]  # only one file can exist here at a time


def record_off():
    sh.touch(settings.ONOFF_PATH + '/stop_record')


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
        sleep(0.1)
        new_file = record_on()
        return new_file
    else:
        return "nothing recording"


def get_recording(file_list_index=0):
    all_recordings = [settings.ARCHIVE_RECORDING_PATH+filename for filename in os.listdir(settings.ARCHIVE_RECORDING_PATH)]
    return sorted(all_recordings, key=os.path.getctime, reverse=True)[file_list_index]


def clean_archive():
    return "done"
