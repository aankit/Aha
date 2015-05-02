import time
import aha

while True:
    refresh_state = aha.refresh_camera()
    if refresh_state:
        last_recording = aha.get_last_recorded()
        while last_recording is None:
            last_recording = aha.get_last_recorded()
        aha.stage_file(last_recording)
    elif aha.get_all_recorded():
        for recording in aha.get_all_recorded():
            aha.stage_file(recording)
    sleep_time = aha.refresh_sleep()
    time.sleep(sleep_time)
